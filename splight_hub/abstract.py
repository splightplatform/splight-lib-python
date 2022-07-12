from pydantic import BaseModel
from typing import List, Type, Dict
from client import AbstractClient
from abc import abstractmethod


class AbstractHubClient(AbstractClient):
    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    @abstractmethod
    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def delete(self, resource_type: Type, id: str) -> None:
        pass

    @abstractmethod
    def update(self, resource_type: Type, id: str, data: Dict) -> BaseModel:
        pass
