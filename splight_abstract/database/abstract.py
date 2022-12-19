from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List
from splight_abstract.client import AbstractClient, QuerySet
from tempfile import NamedTemporaryFile


class AbstractDatabaseClient(AbstractClient):

    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    @abstractmethod
    def _get(self,
             resource_type: Type,
             first: bool = False,
             limit_: int = -1,
             skip_: int = 0,
             deleted: bool = False,
             **kwargs) -> List[BaseModel]:
        pass

    def get(self, resource_type: Type, *args, **kwargs) -> QuerySet:
        return QuerySet(self, resource_type, *args, **kwargs)

    @abstractmethod
    def delete(self, resource_type: Type, id: str) -> None:
        pass

    @abstractmethod
    def count(self, resource_type: Type, **kwargs) -> int:
        pass

    @abstractmethod
    def download(self, instance: BaseModel) -> NamedTemporaryFile:
        pass
