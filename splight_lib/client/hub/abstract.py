from abc import abstractmethod
from typing import Dict, List, Tuple, Type

from pydantic import BaseModel

from splight_lib.abstract.client import AbstractClient, QuerySet


class AbstractHubClient(AbstractClient):
    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    @abstractmethod
    def _get(
        self,
        first=False,
        limit_: int = -1,
        skip_: int = 0,
        **kwargs,
    ) -> List[BaseModel]:
        pass

    @abstractmethod
    def upload(self, data: Dict, files: Dict) -> Tuple:
        pass

    @abstractmethod
    def download(self, data: Dict) -> Tuple:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass

    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass
