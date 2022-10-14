from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, List, Type, Tuple

from pydantic import BaseModel

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
    @abstractmethod
    def upload(self, data: Dict, files: Dict) -> Tuple:
        pass

    @abstractmethod
    def download(self, data: Dict) -> Tuple:
        pass

    @abstractmethod
    def random_picture(self):
        pass

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

    @abstractproperty
    def system(self) -> AbstractHubSubClient:
        pass
