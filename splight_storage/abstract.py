from pydantic import BaseModel
from abc import abstractmethod
from typing import Optional, Type, List
from client import AbstractClient


class AbstractStorageClient(AbstractClient):

    @abstractmethod
    def create(self, instance: BaseModel) -> BaseModel:
        pass

    @abstractmethod
    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def delete(self, resource_type: Type, id: str) -> None:
        pass

    @abstractmethod
    def download(self, filename: str, target: str) -> str:
        pass
