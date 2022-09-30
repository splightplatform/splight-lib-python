from pydantic import BaseModel
from typing import Dict, List, Type
from splight_abstract.hub.abstract import AbstractHubSubClient
from splight_lib import logging
from splight_models import (
    HubNetwork,
    HubAlgorithm,
    HubComponent,
    HubComponentVersion,
    HubConnector,
    HubSystem,
)
from splight_abstract import AbstractHubClient, validate_resource_type


logger = logging.getLogger()


class FakeHubSubClient(AbstractHubSubClient):
    networks = [
        HubNetwork(id="1", name='Net1', description=None, version='01', input=[], type='network'),
        HubNetwork(id="2", name='Net2', description=None, version='01', input=[], type='network'),
        HubNetwork(id="3", name='Net3', description=None, version='01', input=[], type='network')
    ]
    algorithms = [
        HubAlgorithm(id="4", name='Algo1', description=None, version='01', input=[], type='algorithm'),
        HubAlgorithm(id="5", name='Algo2', description=None, version='01', input=[], type='algorithm')
    ]
    connectors = [
        HubConnector(id="6", name='Conn1', description=None, version='01', input=[], type="connector")
    ]
    system = [
        HubSystem(
            id="7",
            name="System1",
            description=None,
            version="01",
            input=[],
            type="system"
        )
    ]
    versions = networks + connectors + algorithms
    grouped_versions = networks + connectors + algorithms
    database: Dict[Type, List[BaseModel]] = {
        HubComponent: grouped_versions,
        HubComponentVersion: versions,
    }
    valid_classes = [
        HubComponent,
        HubComponentVersion
    ]

    allowed_update_fields = ["verification"]

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


class FakeHubClient(AbstractHubClient):

    def __init__(self, *args, **kwargs) -> None:
        self._client = FakeHubSubClient()

    @property
    def all(self) -> AbstractHubSubClient:
        return self._client

    @property
    def mine(self) -> AbstractHubSubClient:
        return self._client

    @property
    def public(self) -> AbstractHubSubClient:
        return self._client

    @property
    def private(self) -> AbstractHubSubClient:
        return self._client

    @property
    def setup(self) -> AbstractHubSubClient:
        return self._client

    @property
    def system(self) -> AbstractHubSubClient:
        return self._client
