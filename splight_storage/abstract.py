from pydantic import BaseModel
from abc import abstractmethod
from typing import Optional, Type, List
from client import AbstractClient
from splight_models import QuerySet


class AbstractStorageClient(AbstractClient):

    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    @abstractmethod
    def _get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def delete(self, resource_type: Type, id: str) -> None:
        pass

    @abstractmethod
    def download(self, filename: str, target: str) -> str:
        pass

    @abstractmethod
    def get_temporary_link(self, filename: str, target: str) -> str:
        pass
