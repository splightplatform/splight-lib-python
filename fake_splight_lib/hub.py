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

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    @validate_resource_type
    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Pulling from hub {resource_type}s")
        queryset = self.database[resource_type]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        return queryset

    @validate_resource_type
    def delete(self, resource_type: Type, id: str) -> None:
        raise NotImplementedError

    def set_impact(self, id: str, impact: int) -> None:
        logger.debug(f"[FAKED] Setting impact {impact} for component id {id}")
        for _, components in self.database.items():
            for component in components:
                if component.id == id:
                    component.impact = impact
                    return

    def set_verification(self, id: str, verification: int) -> None:
        logger.debug(f"[FAKED] Setting verification {verification} for component id {id}")
        for _, components in self.database.items():
            for component in components:
                if component.id == id:
                    component.verification = verification
                    return

