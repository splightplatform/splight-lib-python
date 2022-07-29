from pydantic import BaseModel
from typing import List, Type, Dict
from abc import abstractmethod
from splight_abstract.client import AbstractClient, QuerySet


class AbstractHubClient(AbstractClient):
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
