from client import AbstractClient
from abc import abstractmethod
from typing import List, Type
from pydantic import BaseModel
from splight_models import QuerySet

class AbstractBillingClient(AbstractClient):
    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    @abstractmethod
    def _get(self, resource_type: Type,
             first: bool = False,
             limit_: int = -1,
             skip_: int = 0,
             **kwargs) -> List[BaseModel]:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)