from abc import abstractmethod

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
    ) -> list[BaseModel]:
        pass

    @abstractmethod
    def upload(self, id: str, file_path: str, type: str):
        pass

    @abstractmethod
    def download(self, data: dict) -> tuple:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass

    @abstractmethod
    def save(self, instance: dict) -> dict:
        pass
