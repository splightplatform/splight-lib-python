from abc import ABC, abstractclassmethod, abstractmethod
from pydantic import BaseModel
from typing import List, Dict
from .models import Deployment


class AbstractDeploymentClient(ABC):

    def __init__(self, namespace: str = "default") -> None:
        self.namespace = namespace.lower()

    @abstractclassmethod
    def configure(self, namespace: str, environment: Dict = {}):
        pass

    @abstractmethod
    def create(self, instance: BaseModel) -> Deployment:
        pass

    @abstractmethod
    def apply(self, spec: Deployment) -> Deployment:
        pass

    @abstractmethod
    def get(self, id: str) -> List[Deployment]:
        pass

    @abstractmethod
    def delete(self, deployment: Deployment) -> None:
        pass
