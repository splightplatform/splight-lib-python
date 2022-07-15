from pydantic import BaseModel
from typing import List, Type
from splight_hub.abstract import AbstractHubClient
from splight_lib import logging
from splight_models import *
from client import validate_resource_type


logger = logging.getLogger()


class FakeHubClient(AbstractHubClient):
    networks = [
        HubNetwork(id="1", name='Net1', description=None, version='01', parameters=[]),
        HubNetwork(id="2", name='Net2', description=None, version='01', parameters=[]),
        HubNetwork(id="3", name='Net3', description=None, version='01', parameters=[])
    ]
    algorithms = [
        HubAlgorithm(id="4", name='Algo1', description=None, version='01', parameters=[]),
        HubAlgorithm(id="5", name='Algo2', description=None, version='01', parameters=[])
    ]
    connectors = [
        HubConnector(id="6", name='Conn1', description=None, version='01', parameters=[])
    ]
    database: Dict[Type, List[BaseModel]] = {
        HubNetwork: networks,
        HubAlgorithm: algorithms,
        HubConnector: connectors,
    }
    valid_classes = [
        HubNetwork,
        HubConnector,
        HubAlgorithm
    ]

    allowed_update_fields = ["impact", "verification"]

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    @validate_resource_type
    def _get(self,
             resource_type: Type,
             first=False,
             limit_: int = -1,
             skip_: int = 0,
             **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Pulling from hub {resource_type}s")
        queryset = self.database[resource_type]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if limit_ != -1:
            queryset = queryset[skip_:skip_ + limit_]

        if first:
            return queryset[0] if queryset else None

        return queryset

    @validate_resource_type
    def delete(self, resource_type: Type, id: str) -> None:
        raise NotImplementedError

    @validate_resource_type
    def update(self, resource_type: Type, id: str, data: Dict) -> BaseModel:
        instance = self.get(resource_type, id=id, first=True)
        if not instance:
            raise ValueError(f"{resource_type} with id {id} not found")
        for field in self.allowed_update_fields:
            if field in data:
                setattr(instance, field, data[field])
        return instance
