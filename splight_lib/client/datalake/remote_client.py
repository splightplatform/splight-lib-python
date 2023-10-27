from datetime import datetime, timedelta, timezone
from io import StringIO
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Union

import pandas as pd
from furl import furl
from retry import retry

from splight_lib.abstract.client import AbstractRemoteClient
from splight_lib.auth import SplightAuthToken
from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.client.exceptions import SPLIGHT_REQUEST_EXCEPTIONS
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.restclient import SplightRestClient

logger = get_splight_logger()


class RemoteDatalakeClient(AbstractDatalakeClient, AbstractRemoteClient):
    _PREFIX = "v2/engine/datalake"

    def __init__(
        self, base_url: str, access_id: str, secret_key: str, *args, **kwargs
    ):
        super().__init__()
        self._base_url = furl(base_url)
        token = SplightAuthToken(
            access_key=access_id,
            secret_key=secret_key,
        )
        self._restclient = SplightRestClient()
        self._restclient.update_headers(token.header)
        logger.debug(
            "Remote datalake client initialized.", tags=LogTags.DATALAKE
        )

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def save(
        self,
        collection: str,
        instances: Union[List[Dict], Dict],
    ) -> List[dict]:
        instances = instances if isinstance(instances, list) else [instances]
        url = self._base_url / f"{self._PREFIX}/save/"
        response = self._restclient.post(
            url, params={"source": collection}, json=instances
        )
        response.raise_for_status()
        return instances

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    async def async_save(
        self,
        collection: str,
        instances: Union[List[Dict], Dict],
    ) -> List[dict]:
        instances = instances if isinstance(instances, list) else [instances]
        url = self._base_url / f"{self._PREFIX}/save/"
        response = await self._restclient.async_post(
            url, params={"source": collection}, json=instances
        )
        response.raise_for_status()
        return instances

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
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
        # GET /datalake/data/
        url = self._base_url / f"{self._PREFIX}/data/"

        filters.update(
            {
                "source": collection,
                "output_format": resource_name,
                "sort": sort,
                "limit_": limit_,
                "skip_": skip_,
                "group_id": group_id,
                "group_fields": group_fields,
                # "tzinfo": tzinfo
            }
        )

        params = self._parse_params(**filters)
        response = self._restclient.get(url, params=params)
        response.raise_for_status()
        output = response.json()["results"]

        return output

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
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
        # GET /datalake/data/
        url = self._base_url / f"{self._PREFIX}/data/"

        filters.update(
            {
                "source": collection,
                "output_format": resource_name,
                "sort": sort,
                "limit_": limit_,
                "skip_": skip_,
                "group_id": group_id,
                "group_fields": group_fields,
                # "tzinfo": tzinfo
            }
        )

        params = self._parse_params(**filters)
        response = await self._restclient.async_get(url, params=params)
        response.raise_for_status()
        output = response.json()["results"]

        return output

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def delete(self, collection: str, **kwargs) -> None:
        # DELETE /datalake/delete/
        url = self._base_url / f"{self._PREFIX}/delete/"
        params = {"source": collection}
        response = self._restclient.delete(url, params=params, json=kwargs)
        response.raise_for_status()

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
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
        filters.update(
            {
                "source": collection,
                "output_format": resource_name,
                "sort": sort,
                "group_id": group_id,
                "group_fields": group_fields,
            }
        )

        # GET /datalake/dumpdata/?source=collection
        url = self._base_url / f"{self._PREFIX}/dumpdata/"
        params = self._parse_params(**filters)

        response = self._restclient.get(url, params=params)
        response.raise_for_status()
        logger.debug(
            "Retrieving dataframe from datalake.", tags=LogTags.DATALAKE
        )

        df: pd.DataFrame = pd.DataFrame(pd.read_csv(StringIO(response.text)))
        if df.empty:
            return df
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        return df

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def save_dataframe(self, collection: str, dataframe: pd.DataFrame) -> None:
        logger.debug("Saving dataframe.", tags=LogTags.DATALAKE)

        # POST /datalake/loaddata/
        url = self._base_url / f"{self._PREFIX}/loaddata/"

        tmp_file = NamedTemporaryFile("w")
        with open(tmp_file.name, "wb") as fid:
            dataframe.to_csv(fid)
        response = self._restclient.post(
            url,
            data={"source": collection},
            files={"file": open(tmp_file.name, mode="rb")},
        )
        response.raise_for_status()

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def create_index(self, collection: str, indexes: List[Dict]) -> None:
        # POST /datalake/index/
        logger.debug(
            "Creating index for collection: %s.",
            collection,
            tags=LogTags.DATALAKE,
        )

        url = self._base_url / f"{self._PREFIX}/index/"
        data = {"source": collection, "index": indexes}
        response = self._restclient.post(url, json=data)
        response.raise_for_status()

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def raw_aggregate(
        self, collection: str, pipeline: List[Dict]
    ) -> List[Dict]:
        logger.debug(
            "Aggregate on datalake collection: %s.",
            collection,
            tags=LogTags.DATALAKE,
        )
        # POST /datalake/aggregate/?source=collection
        url = self._base_url / f"{self._PREFIX}/aggregate/"
        params = {"source": collection}
        data = {"pipeline": pipeline}
        response = self._restclient.post(url, params=params, data=data)
        response.raise_for_status()
        return response.json()

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def execute_query(
        self,
        from_timestamp: datetime,
        to_timestamp: Optional[datetime],
        query: Dict,
    ) -> pd.DataFrame:
        url = self._base_url / f"{self._PREFIX}/data/request/csv/"
        to_timestamp = to_timestamp.isoformat() if to_timestamp else None
        data = {
            "from_timestamp": from_timestamp.isoformat(),
            "to_timestamp": to_timestamp,
            "traces": [
                {
                    "ref_id": "output",
                    "type": "QUERY",
                    "expression": None,
                    "pipeline": query,
                }
            ],
        }
        response = self._restclient.post(url, json=data)
        response.raise_for_status()

        df: pd.DataFrame = pd.DataFrame(
            pd.read_csv(StringIO(response.text), index_col=False)
        )
        if df.empty:
            return df
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.drop(labels="Unnamed: 0", axis=1, inplace=True)
        df.set_index("timestamp", inplace=True)
        return df
