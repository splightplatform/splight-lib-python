from abc import abstractmethod
from typing import Any, TypedDict

from splight_lib.abstract.client import AbstractRemoteClient, QuerySet


class Records(TypedDict):
    collection: str
    records: list[dict[str, Any]]


# TODO: Fix this class after delete QuerySet
class AbstractDatalakeClient(AbstractRemoteClient):
    def get(self, *args, **kwargs) -> QuerySet:
        # kwargs["get_func"] = "_get"
        # kwargs["count_func"] = "None"
        # return QuerySet(self, *args, **kwargs)
        return self._get(*args, **kwargs)

    async def async_get(self, *args, **kwargs):
        # TODO: consider using an async QuerySet
        return await self._async_get(*args, **kwargs)

    @abstractmethod
    def save(self, records: Records) -> list[dict]:
        pass

    @abstractmethod
    async def async_save(self, records: Records) -> list[dict]:
        pass

    @abstractmethod
    def _get(self, request: dict) -> list[dict]:
        pass

    @abstractmethod
    async def _async_get(self, request: dict) -> list[dict]:
        pass
