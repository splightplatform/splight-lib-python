import pytz
from splight_lib import logging
from pymongo import MongoClient as PyMongoClient
from typing import Dict, List, Type, Optional
from datetime import datetime
from pydantic import BaseModel
from django.utils import timezone
from .abstract import AbstractDatalakeClient
from splight_datalake.settings import setup
from splight_lib.communication import Variable
from splight_lib.database import TriggerNotification
from client import validate_resource_type, validate_instance_type
utc = pytz.utc


class MongoClient(AbstractDatalakeClient):
    logger = logging.getLogger()

    valid_classes = [Variable, TriggerNotification]

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

    def aggregate(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
        documents = self.db[collection].aggregate(pipeline)
        return documents

    def delete_many(self, collection: str, filters: Dict = {}) -> None:
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
    def get(self, resource_type: Type, from_: datetime = None, to_: datetime = None, first_: bool = False, limit_: int = 50, skip_: int = 0, **kwargs) -> List[BaseModel]:
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        updates = list(self._find(resource_type.__name__, self._get_filters(from_, to_, **kwargs), limit=limit_, skip=skip_, sort=[('timestamp', -1)]))
        result = [resource_type(**update) for update in updates]
        if first_:
            return result[0] if result else None
        return result

    @validate_resource_type
    def save(self, resource_type: Type, instances: List[BaseModel]) -> List[BaseModel]:
        for instance in instances:
            if not isinstance(instance, resource_type):
                raise NotImplementedError
        
        data_list = []
        for instance in instances:
            data = instance.dict()
            data["timestamp"] = datetime.now(tz=utc)
            data_list.append(data)

        self._insert_many(resource_type.__name__, data=data_list)
        return instances