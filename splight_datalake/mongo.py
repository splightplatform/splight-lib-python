import pandas as pd
from bson.codec_options import CodecOptions
from client import validate_resource_type
from datetime import timezone, timedelta
from pymongo import MongoClient as PyMongoClient
from typing import Dict, List, Type
from pydantic import BaseModel
from collections.abc import MutableMapping
from collections import defaultdict
from client import validate_resource_type
from splight_datalake.settings import setup
from splight_lib import logging
from splight_models import Variable, VariableDataFrame, BillingEvent
from .abstract import AbstractDatalakeClient


logger = logging.getLogger()


def flatten_dict(d, parent_key='', sep='__'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class MongoClient(AbstractDatalakeClient):
    valid_classes: List[Type] = [Variable, BillingEvent]
    operation_map: Dict[str, str] = {
        'eq': '$eq',
        'in': '$in',
        'contains': '$regex',
        'gte': '$gte',
        'lte': '$lte',
    }

    def __init__(self, *args, **kwargs) -> None:
        super(MongoClient, self).__init__(*args, **kwargs)
        connection = f'{setup["PROTOCOL"]}://{setup["USER"]}:{setup["PASSWORD"]}@{setup["HOST"]}'
        if setup["PORT"]:
            connection = f'{connection}:{setup["PORT"]}'
        client = PyMongoClient(connection)
        self.db = client[self.namespace]

    def _find(self, collection: str, filters: Dict = None, tzinfo=timezone(timedelta()), **kwargs) -> List[Dict]:
        codec_options = CodecOptions(
            tz_aware=True,
            tzinfo=tzinfo
        )
        documents = self.db.get_collection(
            collection,
            codec_options=codec_options
        ).find(
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

    def _get_filters(self, **kwargs) -> Dict:
        filters: defaultdict = defaultdict(dict)

        for key, value in kwargs.items():
            args = key.split('__')
            oper = args[-1] if args[-1] in self.valid_filters else 'eq'
            args = args if oper == "eq" else args[:-1]
            key = '.'.join(args)
            filters[key][self.operation_map[oper]] = value

        return dict(filters)

    def list_collection_names(self):
        return self.db.list_collection_names()

    def get_unique_keys(self, collection: str, **kwargs):
        docs = list(self._find(
            collection=collection,
            limit=10,
            sort=[('timestamp', -1)],
            filters=self._get_filters(**kwargs)),
        )
        docs = [flatten_dict(d) for d in docs]
        return list(set(key for dic in docs for key in dic.keys()))

    def get_values_for_key(self, collection: str, key: str, **kwargs):
        _key = key.replace('__', '.')
        return self.db[collection].distinct(_key, filter=self._get_filters(**kwargs))

    @validate_resource_type
    def get(self,
            resource_type: Type,
            collection: str = 'default',
            limit_: int = 50,
            skip_: int = 0,
            tzinfo: timezone = timezone(timedelta()),
            **kwargs) -> List[BaseModel]:

        kwargs = self._validated_kwargs(resource_type, **kwargs)
        filters = self._get_filters(**kwargs)
        result = self._find(
            collection=collection,
            filters=filters,
            limit=limit_,
            skip=skip_,
            sort=[('timestamp', -1)],
            tzinfo=tzinfo
        )
        result = [resource_type(**obj) for obj in result]
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

    def get_collection_size_gb(self, collection: str) -> float:
        return self.db.command("collstats", collection)["totalSize"] / (1024 * 1024 * 1024)

    def get_dataframe(self, *args, **kwargs) -> VariableDataFrame:
        _data = self.get(*args, **kwargs)
        _data = pd.json_normalize(
            [d.dict() for d in _data]
        )
        _data = VariableDataFrame(_data)
        if not _data.empty:
            _data.columns = [col.replace("args.", "") for col in _data.columns]
        return _data

    def save_dataframe(self, dataframe: VariableDataFrame, collection: str = 'default') -> None:
        variables = [
            Variable(
                timestamp=pd.to_datetime(row.get("timestamp", index)),
                asset_id=row.get("asset_id", None),
                path=row.get("path", None),
                attribute_id=row.get("attribute_id", None),
                args={col: value for col, value in row.items() if col not in Variable.__fields__}
            ) for index, row in dataframe.iterrows()
        ]
        self.save(Variable, instances=variables, collection=collection)
