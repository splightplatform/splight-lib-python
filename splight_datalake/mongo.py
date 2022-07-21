import re
import pandas as pd
from datetime import datetime
from bson.codec_options import CodecOptions
from client import validate_resource_type
from datetime import timezone, timedelta
from pymongo import MongoClient as PyMongoClient
from typing import Dict, List, Optional, Tuple, Type, Union
from pydantic import BaseModel
from collections.abc import MutableMapping
from collections import defaultdict
from client import validate_resource_type
from splight_datalake.settings import setup
from splight_lib import logging
from splight_models import Variable, VariableDataFrame, Notification, BillingEvent
from .abstract import AbstractDatalakeClient
from splight_models.query import QuerySet

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
    valid_classes: List[Type] = [Variable, Notification, BillingEvent]
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

    def _aggregate(self, collection: str, pipeline: List[Dict], tzinfo=timezone(timedelta())) -> List[Dict]:
        codec_options = CodecOptions(
            tz_aware=True,
            tzinfo=tzinfo
        )
        documents = self.db.get_collection(
            collection,
            codec_options=codec_options
        ).aggregate(
            pipeline
        )
        return documents

    def _delete_many(self, collection: str, filters: Dict = {}) -> None:
        self.db[collection].delete_many(filters)

    def _insert_many(self, collection: str, data: List[Dict], **kwargs) -> None:
        self.db[collection].insert_many(data, **kwargs)

    def __parse_filters(self, **kwargs) -> Dict:
        filters: defaultdict = defaultdict(dict)

        for key, value in kwargs.items():
            args = key.split('__')
            oper = args[-1] if args[-1] in self.valid_filters else 'eq'
            args = args if oper == "eq" else args[:-1]
            key = '.'.join(args)
            filters[key][self.operation_map[oper]] = value

        return dict(filters)

    @staticmethod
    def __parse_sort(sort: List = []):
        _sort = [item.rsplit('__', 1) for item in sort]
        _sort = [(k, -1) if v == 'desc' else (k, 1) if v == 'asc' else None for k, v in _sort]
        _sort = [k for k in _sort if k is not None]
        return _sort

    @staticmethod
    def __parse_group_id(group_id: List = []):
        _group_id = [item.rsplit('__', 1) for item in group_id]
        _group_id = [None if item[0] == 'null' else item for item in _group_id]
        return _group_id

    @staticmethod
    def __parse_group_fields(group_fields):
        _group_id = [item.rsplit('__', 1) for item in group_fields]
        return _group_id

    @staticmethod
    def __get_match_pipeline_step(filters: Dict, **kwargs):
        _match = filters
        return {"$match": _match}

    @staticmethod
    def __get_group_pipeline_step(group_id: Union[List[Tuple], None] = [], group_fields: List[Tuple] = [], **kwargs):
        _group = None
        if not group_id:
            return {"$group": _group}

        if None in group_id:
            _group = {
                "_id": None,
            }
        else:
            _group = {
                "_id": {
                    f"{operator}-{field}": {f"${operator}": f"${field}"}
                    for field, operator in group_id
                },
            }
        _group["_root"] = {"$last": "$$ROOT"}
        for field, operator in group_fields:
            _group[f"agg_{field.replace('.', '__')}"] = {f"${operator}": f"${field.replace('__', '.')}"}
        return {"$group": _group}

    @staticmethod
    def __get_set_pipeline_step(group_id: Union[List[Tuple], None] = [], group_fields: List[Tuple] = [], **kwargs):
        _set = None
        if group_id:
            _set = {
                f"_root.{field.replace('__', '.')}": f"$agg_{field.replace('.', '__')}"
                for field, _ in group_fields
            }
        return {"$set": _set}

    @staticmethod
    def __get_replaceRoot_pipeline_step(group_id: Union[List[Tuple], None] = [], **kwargs):
        _replaceRoot = None
        if group_id:
            # Only want to replace root if we did a group in the past
            _replaceRoot = {"newRoot": "$_root"}
        return {"$replaceRoot": _replaceRoot}

    @staticmethod
    def __get_skip_pipeline_step(skip: Optional[int] = None, **kwargs):
        _skip = skip
        return {"$skip": _skip}

    @staticmethod
    def __get_limit_pipeline_step(limit: Optional[int] = None, **kwargs):
        _limit = limit
        return {"$limit": _limit}

    @staticmethod
    def __get_sort_pipeline_step(sort: Optional[List[Tuple]] = None, **kwargs):
        _sort = sort
        if sort:
            _sort = {
                k: v
                for k, v in sort
            }
        return {"$sort": _sort}

    def _get_pipeline(self, **kwargs):
        pipeline = []
        pipeline.append(self.__get_match_pipeline_step(**kwargs))
        pipeline.append(self.__get_group_pipeline_step(**kwargs))
        pipeline.append(self.__get_set_pipeline_step(**kwargs))
        pipeline.append(self.__get_replaceRoot_pipeline_step(**kwargs))
        pipeline.append(self.__get_skip_pipeline_step(**kwargs))
        pipeline.append(self.__get_sort_pipeline_step(**kwargs))
        pipeline.append(self.__get_limit_pipeline_step(**kwargs))
        # Omit those steps not completed
        pipeline = [step for step in pipeline if all(step.values())]
        return pipeline

    def list_collection_names(self):
        return self.db.list_collection_names()

    def get_unique_keys(self, collection: str, **kwargs):
        docs = list(self._find(
            collection=collection,
            limit=10,
            sort=[('timestamp', -1)],
            filters=self.__parse_filters(**kwargs)),
        )
        docs = [flatten_dict(d) for d in docs]
        return list(set(key for dic in docs for key in dic.keys()))

    def get_values_for_key(self, collection: str, key: str, **kwargs):
        _key = key.replace('__', '.')
        return self.db[collection].distinct(_key, filter=self.__parse_filters(**kwargs))

    @validate_resource_type
    def _get(self,
             resource_type: Type,
             collection: str = 'default',
             limit_: int = 50,
             skip_: int = 0,
             sort: Union[List, str] = ['timestamp__desc'],
             group_id: Union[List, str] = [],
             group_fields: Union[List, str] = [],
             tzinfo: timezone = timezone(timedelta()),
             **kwargs) -> List[BaseModel]:
        instance_kwargs = self._validated_kwargs(resource_type, **kwargs)
        sort = [sort] if isinstance(sort, str) else sort
        group_id = [group_id] if isinstance(group_id, str) else group_id
        group_fields = [group_fields] if isinstance(group_fields, str) else group_fields
        pipeline = self._get_pipeline(
            filters=self.__parse_filters(**instance_kwargs),
            sort=self.__parse_sort(sort=sort),
            group_id=self.__parse_group_id(group_id=group_id),
            group_fields=self.__parse_group_fields(group_fields=group_fields),
            limit=limit_,
            skip=skip_,
        )
        result = self._aggregate(
            collection=collection,
            pipeline=pipeline,
            tzinfo=tzinfo
        )
        result = [resource_type(**obj) for obj in result]
        return result

    @validate_resource_type
    def count(self,
              resource_type: Type,
              collection: str = 'default',
              sort: Union[List, str] = ['timestamp__desc'],
              group_id: Union[List, str] = [],
              group_fields: Union[List, str] = [],
              tzinfo: timezone = timezone(timedelta()),
              **kwargs) -> List[BaseModel]:

        instance_kwargs = self._validated_kwargs(resource_type, **kwargs)
        sort = [sort] if isinstance(sort, str) else sort
        group_id = [group_id] if isinstance(group_id, str) else group_id
        group_fields = [group_fields] if isinstance(group_fields, str) else group_fields
        pipeline = self._get_pipeline(
            filters=self.__parse_filters(**instance_kwargs),
            sort=self.__parse_sort(sort=sort),
            group_id=self.__parse_group_id(group_id=group_id),
            group_fields=self.__parse_group_fields(group_fields=group_fields),
        )
        pipeline.append({"$count": "count"})
        result = self._aggregate(
            collection=collection,
            pipeline=pipeline,
            tzinfo=tzinfo
        )
        result = list(result)
        return result[0]['count'] if result else 0

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

    def get_billing_data(self, collection: str, start: datetime, end: datetime) -> List[Dict]:
        """
        Get billing data from the datalake
        :param collection: collection from where the billing data will be retrieved
        :param start: billing start date
        :param end: billing end date
        :return: List of dicts with one of the following patterns:
            {
                "_id": deployment id,
                events: [{
                    data: dict,
                    type: "component_deployment",
                    event: "create",
                    timestamp: datetime
                },{
                    data: dict,
                    type: "component_deployment",
                    event: "destroy",
                    timestamp: datetime
                }]
            }
            in the case that the billing event stopped in the current billing period (between start,end)
            or
            {
                "_id": deployment id,
                events: [{
                    data: dict,
                    type: "component_deployment",
                    event: "create",
                    timestamp: datetime
                }]
            }
            in the case that the billing event hasn't stopped so far
        """
        return list(self._aggregate(
            collection=collection,
            pipeline=[
            {
                '$match': {'timestamp': {'$lte': end}}
            }, {
                '$group': {
                    '_id': '$data.id', 
                    'events': {'$push': '$$ROOT'}
                }
            }, {
                '$match': {
                    '$or': [
                        {
                            '$and': [
                                {
                                    'events': {'$size': 1}
                                }, {
                                    'events.0.event': 'create'
                                }
                            ]
                        }, {
                            '$and': [
                                {
                                    'events': {'$size': 2}
                                }, {
                                    'events.0.event': 'create'
                                }, {
                                    'events.1.event': 'destroy'
                                }, {
                                    'events.1.timestamp': {'$gte': start}
                                }, {
                                    'events.1.timestamp': {'$lte': end}
                                }
                            ]
                        }
                    ]
                }
            }
            ]
        ))

    def get_components_sizes_gb(self, start: datetime = None, end: datetime = None) -> Dict:
        def parse_timestamp(start, end):
            res = defaultdict(dict)
            if start:
                res["timestamp"]["$gte"] = start
            if end:
                res["timestamp"]["$lte"] = end
            return res

        collections = self.db.collection_names()
        size = 0
        component_sizes: Dict[str, float] = defaultdict(lambda: 0)
        for collection in collections:
            result = self._aggregate(
                collection=collection,
                pipeline=[
                    {"$match": parse_timestamp(start, end)},
                    {"$match": {"instance_id": {"$ne": None}}},
                    {
                        "$group": {
                            "_id": "$instance_id",
                            "size": {"$sum": {"$bsonSize": "$$ROOT"}}
                        }
                    }
                ]
            )
            result = list(result)
            if not result:
                continue
            for component in result:
                component_sizes[component["_id"]] += component["size"]
        result = {}
        for component_id, size in component_sizes.items():
            result[component_id] = size / (1024 * 1024 * 1024)
        return result

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

    def create_index(self, collection: str, index: list) -> None:
        self.db[collection].create_index(index)
