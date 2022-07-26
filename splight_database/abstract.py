from client import AbstractClient
from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List
from splight_models import QuerySet


class AbstractDatabaseClient(AbstractClient):

    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    @abstractmethod
    def _get(self, resource_type: Type,
             first: bool = False,
             limit_: int = -1,
             skip_: int = 0,
             deleted: bool = False,
             **kwargs) -> List[BaseModel]:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    @abstractmethod
    def delete(self, resource_type: Type, id: str) -> None:
        pass

    @abstractmethod
    def count(self, resource_type: Type, **kwargs) -> int:
        pass
