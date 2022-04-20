from pydantic import BaseModel
from typing import List, Type
from splight_database.abstract import AbstractDatabaseClient
from splight_lib import logging
from typing import Dict
from splight_models import *
from collections import defaultdict
from client import validate_instance_type, validate_resource_type

logger = logging.getLogger()


class FakeDatabaseClient(AbstractDatabaseClient):
    database: Dict[Type, List[BaseModel]] = defaultdict(list)
    valid_classes = [
        Network,
        ClientMapping,
        ServerMapping,
        ValueMapping,
        ReferenceMapping,
        ClientConnector,
        ServerConnector,
        Asset,
        Attribute,
        Trigger,
        Tag,
        Namespace,
        Runner,
        Dashboard,
        Tab,
        Filter,
        ChartItem,
        Chart,
    ]

    def _create(self, instance: BaseModel) -> BaseModel:
        instance.id = str(len(self.database[type(instance)]) + 1)
        self.database[type(instance)].append(instance)
        return instance

    @validate_instance_type
    def save(self, instance: BaseModel) -> BaseModel:
        logger.debug(f"[FAKED] Executing save with {instance}")

        mapping_types = [ClientMapping, ValueMapping, ReferenceMapping]
        if type(instance) in mapping_types:
            def same_mapping_in_same_type(x): return x.id != instance.id and x.asset_id == instance.asset_id and x.attribute_id == instance.attribute_id
            def same_mapping(x): return x.asset_id == instance.asset_id and x.attribute_id == instance.attribute_id
            mappings = []
            for mapping_type in mapping_types:
                if type(instance) == mapping_type:
                    mappings.append(len(list(filter(lambda x: same_mapping_in_same_type(x), self.database[mapping_type]))) > 0)
                else:
                    mappings.append(len(list(filter(lambda x: same_mapping(x), self.database[mapping_type]))) > 0)
            if any(mappings):
                raise ValueError("A mapping already exists for this asset and attribute")

        for i, item in enumerate(self.database[type(instance)]):
            if item.id == instance.id:
                self.database[type(instance)][i] = instance
                return instance
        return self._create(instance)

    @validate_resource_type
    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Executing get with {resource_type}")
        queryset = self.database[resource_type]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if first:
            return queryset[0] if queryset else None
        return queryset

    @validate_resource_type
    def delete(self, resource_type: Type, id: str) -> None:
        logger.debug(f"[FAKED] Executing delete with {resource_type} {id}")

        queryset = self.database.get(resource_type, [])
        for i, item in enumerate(queryset):
            if item.id == id:
                del queryset[i]
                return
