from pydantic import BaseModel
from typing import List, Type, Dict
from abc import ABC, abstractmethod, abstractproperty
from splight_abstract.client import AbstractClient, QuerySet


class AbstractHubSubClient(AbstractClient):
    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    @abstractmethod
    def _get(self, resource_type: Type, first=False, limit_: int = -1, skip_: int = 0, **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def delete(self, resource_type: Type, id: str) -> None:
        pass

    @abstractmethod
    def update(self, resource_type: Type, id: str, data: Dict) -> BaseModel:
        pass


class AbstractHubClient(ABC):
    @abstractproperty
    def all(self) -> AbstractHubSubClient:
        pass

    @abstractproperty
    def mine(self) -> AbstractHubSubClient:
        pass

    @abstractproperty
    def public(self) -> AbstractHubSubClient:
        pass

    @abstractproperty
    def private(self) -> AbstractHubSubClient:
        pass

    @abstractproperty
    def setup(self) -> AbstractHubSubClient:
        pass
