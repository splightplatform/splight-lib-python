import uuid
from pydantic import BaseModel
from typing import List, Type
from splight_abstract import (
    AbstractDatabaseClient,
    validate_instance_type,
    validate_resource_type
)
from splight_lib import logging
from typing import Dict
from splight_models import *
from collections import defaultdict
from tempfile import TemporaryFile

logger = logging.getLogger()


class FakeDatabaseClient(AbstractDatabaseClient):
    database: Dict[Type, List[BaseModel]] = defaultdict(list)
    valid_classes = [
        Mapping,
        Asset,
        Attribute,
        File,
        Tag,
        Namespace,
        Component,
        Notification,
        Graph,
        Node,
        Edge,
        BlockchainContract,
        BlockchainContractSubscription,
        Component,
        ComponentObject,
        ComponentCommand,
        Query,
    ]

    def _create(self, instance: BaseModel) -> BaseModel:
        instance.id = str(uuid.uuid4())
        self.database[type(instance)].append(instance)
        return instance

    @validate_instance_type
    def save(self, instance: BaseModel) -> BaseModel:
        logger.debug(f"[FAKED] Executing save with {instance}")

        for i, item in enumerate(self.database[type(instance)]):
            if item.id == instance.id:
                self.database[type(instance)][i] = instance
                return instance
        return self._create(instance)

    @validate_resource_type
    def _get(self, resource_type: Type,
             first: bool = False,
             limit_: int = -1,
             skip_: int = 0,
             **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Executing get with {resource_type}")
        queryset = self.database[resource_type]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if limit_ != -1:
            queryset = queryset[skip_:skip_ + limit_]

        if first:
            return queryset[0] if queryset else None

        return queryset

    @validate_resource_type
    def count(self, resource_type: Type, **kwargs) -> int:
        return len(self._get(resource_type, **kwargs))

    @validate_resource_type
    def delete(self, resource_type: Type, id: str) -> None:
        logger.debug(f"[FAKED] Executing delete with {resource_type} {id}")

        queryset = self.database.get(resource_type, [])
        for i, item in enumerate(queryset):
            if item.id == id:
                del queryset[i]
                return

    @validate_instance_type
    def download(self, instance: BaseModel) -> None:
        f = TemporaryFile("w+")
        data = instance.dict()
        json.dump(data, f, indent=4)
        f.seek(0)
        return f
