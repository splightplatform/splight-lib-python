from pydantic import BaseModel
from typing import List, Type
from splight_database.abstract import AbstractDatabaseClient
from splight_lib import logging
from typing import Dict
from splight_models import *
from collections import defaultdict

logger = logging.getLogger()


class FakeDatabaseClient(AbstractDatabaseClient):
    database: Dict[Type, List[BaseModel]] = defaultdict(list)
    CLASSES = [Network, Namespace, ClientMapping, ServerMapping, ValueMapping, ReferenceMapping, ClientConnector, ServerConnector, Asset, Attribute, Trigger, TriggerGroup, Tag]

    def _create(self, instance: BaseModel) -> BaseModel:
        if type(instance) not in self.CLASSES:
            raise NotImplementedError
        
        instance.id = str(len(self.database[type(instance)])+1)
        self.database[type(instance)].append(instance)
        return instance


    def save(self, instance: BaseModel) -> BaseModel:
        logger.debug(f"[FAKED] Executing save with {instance}")
        if type(instance) not in self.CLASSES:
            raise NotImplementedError
        
        mapping_types = [ClientMapping, ValueMapping, ReferenceMapping]
        if type(instance) in mapping_types:
            same_mapping_in_same_type = lambda x : x.id != instance.id and x.asset_id == instance.asset_id and x.attribute_id == instance.attribute_id
            same_mapping = lambda x : x.asset_id == instance.asset_id and x.attribute_id == instance.attribute_id
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


    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Executing get with {resource_type}")
        if resource_type not in self.CLASSES:
            raise NotImplementedError

        queryset = self.database[resource_type]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if first:
            return queryset[0] if queryset else None
        return queryset


    def delete(self, resource_type: Type, id: str) -> None:
        logger.debug(f"[FAKED] Executing delete with {resource_type} {id}")
        if resource_type not in self.CLASSES:
            raise NotImplementedError

        queryset = self.database.get(resource_type, [])
        for i, item in enumerate(queryset):
            if item.id == id:
                del queryset[i]
                return
        
