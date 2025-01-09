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
