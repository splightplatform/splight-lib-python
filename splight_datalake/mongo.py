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
from splight_lib.database import Notification
from client import validate_resource_type, validate_instance_type
utc = pytz.utc


class MongoClient(AbstractDatalakeClient):
    logger = logging.getLogger()

    valid_classes = [Variable, Notification]

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


    def _get_filters(self, instance: BaseModel, fields: List[str], from_: Optional[datetime], to_: Optional[datetime]) -> Dict:
        if not fields:
            fields = list(instance.__fields__.keys())
        timestamp = dict()
        if from_:
            timestamp["$gte"] = from_
        if to_:
            timestamp["$lte"] = to_
        
        filters = {}
        for field in fields:
            if field in instance.__fields__:
                filters[field] = getattr(instance, field)
        if timestamp:
            filters["timestamp"] = timestamp

        return filters

    @validate_resource_type
    def get(self,
        resource_type: Type,
        instances: List[BaseModel],
        fields: List[str] = [],
        limit: Optional[int] = 1,
        from_: Optional[datetime] = None,
        to_: Optional[datetime] = None) -> List[BaseModel]:
        
        data = []
        for instance in instances:
            validate_instance_type(instance)
            updates = list(self._find(resource_type.__name__, self._get_filters(instance, fields, from_, to_), limit=limit, sort=[('timestamp', -1)]))
            for update in updates:
                data.append(resource_type(**update))

        return data

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