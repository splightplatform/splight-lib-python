from abc import ABC, abstractmethod, abstractproperty
from functools import wraps
from typing import Callable, Dict, List, Tuple, Type

from pydantic import BaseModel
from splight_lib.abstract.client import AbstractClient, QuerySet


def validate_client_resource_type(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, resource_type: Type, *args, **kwargs):
        if resource_type not in self.valid_classes:
            raise NotImplementedError(
                f"Not a valid resource_type: {resource_type.__name__}"
            )
        return func(self, resource_type, *args, **kwargs)

    return wrapper


class AbstractHubSubClient(AbstractClient):
    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    @abstractmethod
    def _get(
        self,
        resource_type: Type,
        first=False,
        limit_: int = -1,
        skip_: int = 0,
        **kwargs,
    ) -> List[BaseModel]:
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
