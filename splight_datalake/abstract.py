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
    def get(self, resource_type: Type, instances: List[BaseModel], fields: List[str] ,limit: Optional[int] = 1, from_: Optional[datetime] = None, to_: Optional[datetime] = None) -> List[BaseModel]:
        pass