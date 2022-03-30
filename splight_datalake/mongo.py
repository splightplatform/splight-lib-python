import pytz
import pandas as pd
from pymongo import MongoClient as PyMongoClient
from typing import Dict, List, Type, Optional
from datetime import datetime
from pydantic import BaseModel
from django.utils import timezone
from client import validate_resource_type, validate_instance_type
from splight_datalake.settings import setup
from splight_lib import logging
from splight_models import Variable, VariableDataFrame, TriggerNotification
from .abstract import AbstractDatalakeClient


logger = logging.getLogger()


class MongoClient(AbstractDatalakeClient):
    DEFAULT_COLLECTION = "Variable" # TODO define this
    valid_classes = [Variable]

    def __init__(self, *args, **kwargs) -> None:
        super(MongoClient, self).__init__(*args, **kwargs)
        connection = f'{setup["PROTOCOL"]}://{setup["USER"]}:{setup["PASSWORD"]}@{setup["HOST"]}'
        if setup["PORT"]:
            connection = f'{connection}:{setup["PORT"]}'
        client = PyMongoClient(connection)
        self.db = client[self.namespace]

    def _find(self, collection: str, filters: Dict = None, **kwargs) -> List[Dict]:
        documents = self.db[collection].find(
            filter=filters,
            return_key=False,
            **kwargs
        )
        return documents

    def _aggregate(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
        documents = self.db[collection].aggregate(pipeline)
        return documents

    def _delete_many(self, collection: str, filters: Dict = {}) -> None:
        self.db[collection].delete_many(filters)

    def _insert_many(self, collection: str, data: List[Dict], **kwargs) -> None:
        self.db[collection].insert_many(data, **kwargs)

    def _get_filters(self, from_: Optional[datetime], to_: Optional[datetime], **kwargs) -> Dict:
        timestamp = dict()
        if from_:
            timestamp["$gte"] = from_
        if to_:
            timestamp["$lte"] = to_
        if timestamp:
            kwargs["timestamp"] = timestamp

        special_filters = [key for key in kwargs.keys() if key.endswith(("__in", "__contains"))]
        for key in special_filters:
            if key.endswith("__in"):
                kwargs[key[:-len("__in")]] = {"$in": kwargs[key]}
                kwargs.pop(key)
            elif key.endswith("__contains"):
                kwargs[key[:-len("__contains")]] = {"$regex": kwargs[key]}
                kwargs.pop(key)
        return kwargs

    @validate_resource_type
    def get(self,
            resource_type: Type,
            collection: str = 'default',
            from_: datetime = None,
            to_: datetime = None,
            first: bool = False,
            limit_: int = 50,
            skip_: int = 0,
            **kwargs) -> List[BaseModel]:
        # TODO implement from_ to_ with timestamp__gt timestamp__lt
        # TODO first limit_ skip_ is redundant choose one.
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        updates = list(self._find(
            collection=collection,
            filters=self._get_filters(from_, to_, **kwargs),
            limit=limit_,
            skip=skip_,
            sort=[('timestamp', -1)])
        )
        result = [resource_type(**update) for update in updates]
        if first:
            return [result[0]] if result else None
        return result

    @validate_resource_type
    def save(self,
             resource_type: Type,
             instances: List[BaseModel],
             collection: str = 'default') -> List[BaseModel]:
        # TODO @validate_instances_type
        for instance in instances:
            if not isinstance(instance, resource_type):
                raise NotImplementedError(f"Cant ingest {type(instance)} in datalake")

        self._insert_many(collection, data=[d.dict() for d in instances])
        return instances

    def get_dataframe(self, variable: Variable, freq="H", collection: str = 'default') -> VariableDataFrame:
        _data = self.get(
            Variable,
            asset_id=variable.asset_id,
            attribute_id=variable.attribute_id,
            collection=collection
        )
        _data = pd.json_normalize(
            [d.dict() for d in _data]
        )
        if not _data.empty:
            _data = _data.drop(["asset_id", "attribute_id", "path"], axis=1)
            _data.timestamp = _data.timestamp.dt.round(freq=freq)
            _data = _data.groupby(['timestamp'], as_index=True).mean()
            _data.columns = [col.replace("args.value", variable.attribute_id) for col in _data.columns]
        return _data

    def save_dataframe(self, dataframe: VariableDataFrame, collection: str = 'default') -> None:
        for index, row in dataframe.iterrows():
            variables = [
                Variable(
                    timestamp=pd.to_datetime(row.get("timestamp", index)),
                    asset_id=row.get("asset_id", None),
                    path=row.get("path", None),
                    attribute_id=col,
                    args={"value": row.get(col)}
                )
                for col in row.keys() if col not in Variable.__fields__
            ]
            self.save(Variable, instances=variables, collection=collection)
