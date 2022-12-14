import pandas as pd
import operator
import os
import json
from collections import defaultdict
from collections.abc import MutableMapping
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Dict, List, Any, Union
from splight_models import VariableDataFrame, Query, DatalakeModel
from splight_lib import logging
from splight_lib.settings import SPLIGHT_HOME
from splight_abstract.datalake import (
    AbstractDatalakeClient,
    validate_resource_type,
    validate_instance_type,
    QuerySet
)


DATALAKE_HOME = os.path.join(SPLIGHT_HOME, "datalake")
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


class FakeDatalakeClient(AbstractDatalakeClient):
    extra_operators = {
        "in": lambda x, y: x in y,
        "contains": lambda x, y: y in x,
        "gte": lambda x, y: x >= y,
        "lte": lambda x, y: x <= y,
    }

    def __init__(self, namespace: str = 'default', *args, **kwargs) -> None:
        super(FakeDatalakeClient, self).__init__(namespace, *args, **kwargs)
        self.collections = defaultdict(list)
        self._default_load()

    @staticmethod
    def _write_to_collection(collection: str, data: List[dict]) -> None:
        os.makedirs(DATALAKE_HOME, exist_ok=True)
        col_file = os.path.join(DATALAKE_HOME, collection)
        _prev_data = []
        if os.path.exists(col_file):
            with open(col_file, 'r+') as f:
                content = f.read()
                _prev_data = json.loads(content) if content else []
        data = _prev_data + data
        with open(col_file, 'w+') as f:
            f.write(json.dumps(data, indent=4, sort_keys=True, default=str))

    @staticmethod
    def _date_hook(json_dict):
        timeformat = "%Y-%m-%d %H:%M:%S.%f%z"
        for (key, value) in json_dict.items():
            try:
                json_dict[key] = datetime.strptime(value, timeformat)
            except:
                pass
        return json_dict

    @staticmethod
    def _read_from_collection(collection: str) -> List[dict]:
        os.makedirs(DATALAKE_HOME, exist_ok=True)
        col_file = os.path.join(DATALAKE_HOME, collection)
        content = ''
        if os.path.exists(col_file):
            with open(col_file, 'r+') as f:
                content = f.read()
        return json.loads(content, object_hook=FakeDatalakeClient._date_hook) if content else []

    @staticmethod
    def _resolve_filter(keys: List[str], value: Any, oper: str):
        def inner(x: Dict) -> bool:
            for key in keys:
                if not isinstance(x, dict) or not key in x:
                    return False
                x = x[key]

            if oper in FakeDatalakeClient.extra_operators:
                return FakeDatalakeClient.extra_operators[oper](x, value)
            return getattr(operator, oper)(x, value)

        return inner

    def _default_load(self):
        data = [
            {
                "_id": "jashdasd",
                "asset_id": "1",
                "attribute_id": "1",
                "args": {
                    "value": 1
                },
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "_id": "jashdasd",
                "asset_id": "1",
                "attribute_id": "1",
                "args": {
                    "value": 4
                },
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        self._write_to_collection('Splight.Number', data)

    def _find(self, collection: str, filters: List = [], **kwargs) -> List[Dict]:
        values: List[Dict] = self._read_from_collection(collection)
        values = [v for v in values if all(f(v) for f in filters)]
        return values

    def _parse_filters(self, **kwargs) -> List:
        filters: List = []
        for key, value in kwargs.items():
            args: List[str] = key.split('__')
            oper = args[-1] if args[-1] in self.valid_filters else 'eq'
            args = args if oper == 'eq' else args[:-1]
            filters.append(self._resolve_filter(args, value, oper))

        return filters

    def _raw_get(self,
                 collection: str,
                 limit_: int = 50,
                 skip_: int = 0,
                 sort: Union[List, str] = ['timestamp__desc'],
                 group_id: Union[List, str] = [],
                 group_fields: Union[List, str] = [],
                 tzinfo: timezone = None,
                 **kwargs) -> List[BaseModel]:

        if group_id or group_fields or tzinfo:
            raise NotImplementedError(f"Not implemented yet in fake version. Try removing group_ and tzinfo fields")

        result = self._find(collection, filters=self._parse_filters(**kwargs))

        if limit_ == -1:
            return result[skip_:]

        return result[skip_:skip_ + limit_]

    def _raw_save(self, instances: List[Dict], collection: str) -> List[Dict]:
        return self._write_to_collection(collection, instances)

    @validate_resource_type
    def get(self, resource_type: DatalakeModel, *args, **kwargs) -> QuerySet:
        kwargs["get_func"] = "_raw_get"
        kwargs["count_func"] = "None"
        kwargs["collection"] = resource_type.Meta.collection_name
        return QuerySet(self, *args, **kwargs)

    def get_output(self, query: Query) -> List[Dict]:
        # TODO this is not ok. It should return QuerySet
        return self._raw_get(
            collection=query.source,
            limit_=query.limit,
            skip_=query.skip,
            sort=query.sort,
            add_fields=query.add_fields,
            group_id=query.group_id,
            group_fields=query.group_fields,
            rename_fields=query.rename_fields,
            project_fields=query.project_fields,
            tzinfo=timezone(timedelta(hours=query.timezone_offset)),
            **query.filters
        )

    @validate_resource_type
    def get_dataframe(self, resource_type: DatalakeModel, *args, **kwargs) -> VariableDataFrame:
        logger.info(f"[FAKED] getting dataframe {args}, {kwargs}")
        kwargs["collection"] = resource_type.Meta.collection_name
        _data = self._raw_get(*args, **kwargs)
        _data = pd.DataFrame(_data)
        _data.set_index('timestamp', inplace=True)
        return _data

    def get_dataset(self, queries: List[Dict]) -> pd.DataFrame:
        # TODO make this work with List[Query] objects
        logger.info(f"[FAKED] getting dataset {queries}")
        dfs = [self.get_dataframe(**query) for query in queries]
        return pd.concat(dfs, axis=1)

    @validate_resource_type
    def save_dataframe(self, resource_type: DatalakeModel, dataframe: pd.DataFrame) -> None:
        logger.info(f"[FAKED] saving dataframe {dataframe.columns}")
        collection = resource_type.Meta.collection_name
        data = dataframe.reset_index().to_dict(orient="records")
        self._raw_save(instances=data, collection=collection)

    @validate_instance_type
    def save(self, instances: List[BaseModel]) -> List[BaseModel]:
        logger.info(f"[FAKED] Saving instances {instances}")
        if not instances:
            return instances
        resource_type = instances[0].__class__
        collection = resource_type.Meta.collection_name
        return self._raw_save(instances=instances, collection=collection)

    @validate_resource_type
    def delete(self, resource_type: DatalakeModel, **kwargs) -> None:
        logger.info(f"[FAKED] Deleting from {resource_type}")
        raise NotImplementedError

    def create_index(self, collection: str, index: list) -> None:
        logger.info(f"[FAKED] creating index {collection} {index}")

    def raw_aggregate(
        self, collection: str, pipeline: List[Dict]
    ) -> List[Dict]:
        logger.info(f"[FAKED] pipeline {collection} {pipeline}")
        return []
