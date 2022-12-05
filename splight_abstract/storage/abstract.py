from abc import abstractmethod
from pydantic import BaseModel
from typing import Optional, Type, List
from splight_abstract.client import AbstractClient, QuerySet


class AbstractStorageClient(AbstractClient):

    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        kwargs["get_func"] = "_get"
        kwargs["count_func"] = "None"
        return QuerySet(self, *args, **kwargs)

    @abstractmethod
    def _get(self, resource_type: Type, first=False, prefix: Optional[str] = None, limit_: int = -1, skip_: int = 0, **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def copy(self, old_name: str, new_name: str):
        pass

    @abstractmethod
    def delete(self, resource_type: Type, id: str) -> None:
        pass

    @abstractmethod
    def download(self, resource_type: Type, id: str, target: str) -> str:
        pass

    @abstractmethod
    def get_temporary_link(self, filename: str, target: str) -> str:
        pass
