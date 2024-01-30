from abc import abstractmethod
from typing import Dict, List, Union

import pandas as pd

from splight_lib.abstract.client import AbstractRemoteClient, QuerySet
from splight_lib.constants import DEFAULT_COLLECTION, DEFAULT_SORT_FIELD


class AbstractDatalakeClient(AbstractRemoteClient):
    def get(self, *args, **kwargs) -> QuerySet:
        kwargs["get_func"] = "_get"
        kwargs["count_func"] = "None"
        return QuerySet(self, *args, **kwargs)

    async def async_get(self, *args, **kwargs):
        # TODO: consider using an async QuerySet
        return await self._async_get(*args, **kwargs)

    @abstractmethod
    def save(
        self, collection: str, instances: Union[List[Dict], Dict]
    ) -> List[dict]:
        pass

    @abstractmethod
    async def async_save(
        self, collection: str, instances: Union[List[Dict], Dict]
    ) -> List[Dict]:
        pass

    @abstractmethod
    def _get(
        self,
        match: Dict[str, str],
        collection: str = DEFAULT_COLLECTION,
        sort_field: str = DEFAULT_SORT_FIELD,
        sort_direction: int = -1,
        limit: int = 10000,
        **filters,
    ) -> List[Dict]:
        pass

    @abstractmethod
    async def _async_get(
        self,
        match: Dict[str, str],
        collection: str = DEFAULT_COLLECTION,
        sort_field: str = DEFAULT_SORT_FIELD,
        sort_direction: int = -1,
        limit: int = 10000,
        **filters,
    ) -> List[Dict]:
        pass

    @abstractmethod
    def save_dataframe(
        self, dataframe: pd.DataFrame, collection: str = DEFAULT_COLLECTION
    ) -> None:
        pass

    @abstractmethod
    def get_dataframe(
        self,
        match: Dict[str, str],
        sort_field: str = DEFAULT_SORT_FIELD,
        sort_direction: int = -1,
        limit: int = 10000,
        **filters,
    ) -> pd.DataFrame:
        pass
