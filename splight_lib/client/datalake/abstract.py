from abc import abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union

import pandas as pd

from splight_lib.abstract.client import AbstractRemoteClient, QuerySet


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
    ) -> List[dict]:
        pass

    @abstractmethod
    def delete(self, collection: str, **kwargs) -> None:
        pass

    @abstractmethod
    def get_dataframe(
        self,
        resource_name: str,
        collection: str,
        sort: Union[List, str] = ["timestamp__desc"],
        group_id: Optional[Union[List, str]] = None,
        group_fields: Optional[Union[List, str]] = None,
        tzinfo: timezone = timezone(timedelta()),
        **filters,
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def save_dataframe(self, collection: str, dataframe: pd.DataFrame) -> None:
        pass

    @abstractmethod
    def create_index(self, collection: str, indexes: List[Dict]) -> None:
        pass

    @abstractmethod
    def _raw_get(
        self,
        resource_name: str,
        collection: str,
        limit_: int = 50,
        skip_: int = 0,
        sort: Union[List, str] = ["timestamp__desc"],
        group_id: Optional[Union[List, str]] = None,
        group_fields: Optional[Union[List, str]] = None,
        tzinfo: timezone = timezone(timedelta()),
        **filters,
    ) -> List[Dict]:
        pass

    @abstractmethod
    async def _async_raw_get(
        self,
        resource_name: str,
        collection: str,
        limit_: int = 50,
        skip_: int = 0,
        sort: Union[List, str] = ["timestamp__desc"],
        group_id: Optional[Union[List, str]] = None,
        group_fields: Optional[Union[List, str]] = None,
        tzinfo: timezone = timezone(timedelta()),
        **filters,
    ) -> List[Dict]:
        pass

    @abstractmethod
    def execute_query(
        self,
        from_timestamp: datetime,
        to_timestamp: Optional[datetime],
        query: Dict,
    ) -> pd.DataFrame:
        pass
