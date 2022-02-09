from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Type


class AbstractDeploymentClient(ABC):

    def __init__(self, namespace: str = "default") -> None:
        self.namespace = namespace.lower()

    @abstractmethod
    def create(self, instance: BaseModel) -> None:
        pass

    @abstractmethod
    def get(self,  resource_type: Type, resource_id: str) -> List[BaseModel]:
        pass

    @abstractmethod
    def delete(self, resource_type: Type, resource_id: str) -> None:
        pass
