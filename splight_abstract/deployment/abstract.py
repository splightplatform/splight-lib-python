from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List, Optional
from splight_abstract.client import AbstractClient, QuerySet


class AbstractDeploymentClient(AbstractClient):
    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    @abstractmethod
    def _get(self, resource_type: Type, id: str = '', first=False, limit_: int = -1, skip_: int = 0, **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def delete(self, resource_type: Type, id: str) -> None:
        pass

    def get_deployment_logs(self, id: str, limit: Optional[int] = None, since: Optional[str] = None, previous: bool = False) -> List[str]:
        pass
