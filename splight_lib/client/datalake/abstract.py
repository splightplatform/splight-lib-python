from abc import abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union

import pandas as pd

from splight_lib.abstract.client import AbstractRemoteClient, QuerySet
from splight_lib.client.datalake.schemas import DataRequest


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
    def raw_get(
        self,
        data_request: DataRequest,
    ) -> List[Dict]:
        pass

    @abstractmethod
    async def _async_get(
        self,
        asset: str,
        attribute: str,
        collection: str = "default",
        sort_field: str = "timestamp",
        sort_direction: int = -1,
        limit: int = 10000,
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
