from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List
from .models import Deployment, Namespace


class AbstractDeploymentClient(ABC):

    def __init__(self, namespace: str = "default") -> None:
        self.namespace = namespace.lower()

    @abstractmethod
    def create(self, instance: BaseModel) -> Deployment:
        pass

    @abstractmethod
    def get(self, id: str) -> List[Deployment]:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass

    @abstractmethod
    def create_namespace(self, instance: BaseModel) -> Namespace:
        pass

    @abstractmethod
    def get_namespace(self, id: str) -> List[Namespace]:
        pass

    @abstractmethod
    def delete_namespace(self, id: str) -> None:
        pass
