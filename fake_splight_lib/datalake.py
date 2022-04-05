import pandas as pd
import operator
import os
import json
from collections import defaultdict
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List, Type, Optional
from splight_models import Variable, VariableDataFrame
from splight_lib import logging
from splight_lib.settings import SPLIGHT_HOME


DATALAKE_HOME = os.path.join(SPLIGHT_HOME, "datalake")
logger = logging.getLogger()


class FakeDatalakeClient:
    def __init__(self, namespace: str = 'default') -> None:
        self.collections = defaultdict(list)
        self._default_load()

    @staticmethod
    def _write_to_collection(collection: str, data: List[dict]) -> None:
        os.makedirs(DATALAKE_HOME, exist_ok=True)
        col_file = os.path.join(DATALAKE_HOME, collection)
        if os.path.exists(col_file):
            with open(col_file, 'r+') as f:
                _prev_data = json.loads(f.read())
                data = _prev_data + data
        with open(col_file, 'w+') as f:
            f.write(json.dumps(data, indent=4, sort_keys=True, default=str))

    @staticmethod
    def _read_from_collection(collection: str) -> List[dict]:
        os.makedirs(DATALAKE_HOME, exist_ok=True)
        col_file = os.path.join(DATALAKE_HOME, collection)
        with open(col_file, 'r+') as f:
            return json.loads(f.read())

    def _default_load(self):
        data = [
            {
                "_id": "jashdasd",
                "asset_id": "1",
                "attribute_id": "1",
                "args": {
                    "value": 1
                },
                "timestamp": datetime.now()
            },
            {
                "_id": "jashdasd",
                "asset_id": "1",
                "attribute_id": "1",
                "args": {
                    "value": 4
                },
                "timestamp": datetime.now()
            }
        ]
        self._write_to_collection('default', data)

    def _find(self, collection: str, filters: Dict = {}, **kwargs) -> List[Dict]:
        values = self._read_from_collection(collection)
        for key, op, value in filters:
            values = [v for v in values if op(v.get(key), value)]
        return values

    @staticmethod
    def _parse_filters(**kwargs) -> Dict:
        # overload operator class with methods not covered
        setattr(operator, "in", lambda x, y: x in y)
        setattr(operator, "gte", operator.ge)
        setattr(operator, "lte", operator.le)
        setattr(operator, "like", lambda x, y: x in y)
        setattr(operator, "ilike", lambda x, y: x.lower() in y.lower())
        filters = []
        for key, value in kwargs.items():
            if "__" not in key:
                filters.append((key, operator.eq, value))
                continue

            key, op = key.split("__")
            filters.append((key, getattr(operator, op), value))
        return filters

    def get(self,
            resource_type: Type,
            collection: str = "default",
            from_: datetime = None,
            to_: datetime = None,
            first: bool = False,
            limit_: int = 100,
            skip_: int = 0,
            **kwargs) -> List[BaseModel]:
        if from_:
            kwargs["timestamp__gt"] = from_
        if to_:
            kwargs["timestamp__lt"] = to_
        return [resource_type(**v) for v in self._find(collection, filters=self._parse_filters(**kwargs))]

    def save(self, resource_type: Type, instances: List[BaseModel], collection: str = "default") -> List[BaseModel]:
        data = [instance.dict() for instance in instances]
        self._write_to_collection(collection, data)

    def get_dataframe(self, *args, **kwargs) -> VariableDataFrame:
        logger.info(f"[FAKED] getting dataframe {args}, {kwargs}")
        _data = self.get(*args, **kwargs)
        _data = pd.json_normalize(
            [d.dict() for d in _data]
        )
        _data = VariableDataFrame(_data)
        if not _data.empty:
            _data.columns = [col.replace("args.", "") for col in _data.columns]
        return _data

    def save_dataframe(self, dataframe: VariableDataFrame, collection: str = 'default') -> None:
        logger.info(f"[FAKED] saving dataframe {dataframe.columns}")
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
