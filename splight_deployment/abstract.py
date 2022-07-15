from client import AbstractClient
from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List, Optional
from splight_models import QuerySet


class AbstractDeploymentClient(AbstractClient):
    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    @abstractmethod
    def _get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def delete(self, resource_type: Type, id: str) -> None:
        pass

    def get_deployment_logs(self, id: str, limit: Optional[int] = None, since: Optional[str] = None) -> List[str]:
        pass
