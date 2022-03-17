from client import AbstractClient
from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List, Optional
from datetime import datetime


class AbstractDatalakeClient(AbstractClient):

    @abstractmethod
    def save(self, resource_type: Type, instances: List[BaseModel]) -> List[BaseModel]:
        pass

    @abstractmethod
    def get(self, resource_type: Type, from_: datetime = None, to_: datetime = None, first: bool = False, limit_: int = 50, skip_: int = 0, **kwargs) -> List[BaseModel]:
        pass