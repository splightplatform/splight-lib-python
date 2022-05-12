from pydantic import BaseModel
from typing import List, Type
from splight_hub.abstract import AbstractHubClient
from splight_lib import logging
from splight_models import *
from client import validate_resource_type


logger = logging.getLogger()


class FakeHubClient(AbstractHubClient):
    database: Dict[Type, List[BaseModel]] = defaultdict(list)
    valid_classes = [
        Network,
        Connector,
        Algorithm
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
