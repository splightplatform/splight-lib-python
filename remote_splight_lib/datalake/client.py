from datetime import timedelta, timezone
from io import StringIO
from tempfile import NamedTemporaryFile
from typing import Dict, List, Type, Union

import pandas as pd
import json
from furl import furl
from pydantic import BaseModel
from requests import Session

from remote_splight_lib.auth import SplightAuthToken
from remote_splight_lib.settings import settings
from splight_abstract.remote import AbstractRemoteClient
from splight_abstract.datalake import AbstractDatalakeClient, validate_resource_type


class DatalakeClient(AbstractDatalakeClient, AbstractRemoteClient):

    _PREFIX = "datalake"

    def __init__(self, namespace: str = "default"):
        super(DatalakeClient, self).__init__(namespace=namespace)
        self._base_url = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._session = Session()
        self._session.headers.update(token.header)

    def save(
        self,
        instances: List[BaseModel],
        collection: str = "default",
    ) -> List[BaseModel]:
        # POST /datalake/save/
        url = self._base_url / f"{self._PREFIX}/save/"
        data = [json.loads(model.json()) for model in instances]
        response = self._session.post(
            url, params={"source": collection}, json=data
        )
        response.raise_for_status()
        return instances

    def raw_save(
        self,
        instances: List[Dict],
        collection: str = "default",
    ) -> List[Dict]:
        # POST /datalake/save/
        url = self._base_url / f"{self._PREFIX}/save/"
        response = self._session.post(
            url, params={"source": collection}, json=instances
        )
        response.raise_for_status()
        return instances

    def _raw_get(self,
                 collection: str = 'default',
                 limit_: int = 50,
                 skip_: int = 0,
                 sort: Union[List, str] = ['timestamp__desc'],
                 group_id: Union[List, str] = [],
                 group_fields: Union[List, str] = [],
                 tzinfo: timezone = timezone(timedelta()),
                 **kwargs) -> List[BaseModel]:
        # /datalake/data/
        url = self._base_url / f"{self._PREFIX}/data/"
        kwargs.update(
            {
                "source": collection,
                "limit_": limit_,
                "skip_": skip_,
                "sort": sort,
                "group_id": group_id,
                "group_fields": group_fields,
                # "tzinfo": tzinfo
            }
        )
        params = self._parse_params(**kwargs)
        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response.json()["results"]

    @validate_resource_type
    def _get(
        self,
        resource_type: Type,
        collection: str = "default",
        limit_: int = 50,
        skip_: int = 0,
        sort: Union[List, str] = ["timestamp__desc"],
        group_id: Union[List, str] = [],
        group_fields: Union[List, str] = [],
        tzinfo: timezone = timezone(timedelta()),
        **kwargs,
    ) -> List[BaseModel]:
        # /datalake/data/
        url = self._base_url / f"{self._PREFIX}/data/"
        valid_kwargs = self._validated_kwargs(resource_type, **kwargs)
        valid_kwargs.update(
            {
                "source": collection,
                "limit_": limit_,
                "skip_": skip_,
                "sort": sort,
                "group_id": group_id,
                "group_fields": group_fields,
                # "tzinfo": tzinfo
            }
        )
        params = self._parse_params(valid_kwargs)
        response = self._session.get(url, params=params)
        response.raise_for_status()
        output = [
            resource_type.parse_obj(item)
            for item in response.json()["results"]
        ]
        return output

    def get_dataframe(
        self,
        freq: str = None,
        collection: str = "default",
        **kwargs
    ) -> pd.DataFrame:
        # GET /datalake/dumpdata/?source=collection
        url = self._base_url / f"{self._PREFIX}/dumpdata/"
        kwargs.update({"source": collection})
        kwargs.update({"freq": freq})
        params = self._parse_params(**kwargs)
        response = self._session.get(
            url, params=params
        )
        response.raise_for_status()

        df: pd.DataFrame = pd.DataFrame(pd.read_csv(StringIO(response.text)))
        if df.empty:
            return df
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        return df

    def save_dataframe(
        self, dataframe: pd.DataFrame, collection: str = 'default'
    ) -> None:
        # POST /datalake/loaddata/
        url = self._base_url / f"{self._PREFIX}/loaddata/"

        tmp_file = NamedTemporaryFile("w")
        with open(tmp_file.name, "wb") as fid:
            dataframe.to_csv(fid)

        response = self._session.post(
            url,
            data={"source": collection},
            files={"file": open(tmp_file.name)},
        )
        response.raise_for_status()

    def list_collection_names(self) -> List[str]:
        # GET /datalake/source
        url = self._base_url / f"{self._PREFIX}/source/"
        response = self._session.get(url)
        response.raise_for_status()
        sources = [source["source"] for source in response.json()["results"]]
        return sources

    def get_unique_keys(self, collection: str) -> List[str]:
        # GET /datalake/key/?source=collection
        url = self._base_url / f"{self._PREFIX}/key/"
        response = self._session.get(url, params={"source": collection})
        response.raise_for_status()
        keys = list({key["key"] for key in response.json()["results"]})
        return keys

    def get_values_for_key(self, collection: str, key: str) -> List[str]:
        # GET /datalake/value/?source=collection&key=key
        url = self._base_url / f"{self._PREFIX}/value/"
        params = {"source": collection, "key": key}
        response = self._session.get(url, params=params)
        response.raise_for_status()
        values = [value["value"] for value in response.json()["results"]]
        return values

    # Subject to incompatibility by implementation
    def raw_aggregate(
        self, collection: str, pipeline: List[Dict]
    ) -> List[Dict]:
        # POST /datalake/aggregate/?source=collection
        url = self._base_url / f"{self._PREFIX}/aggregate/"
        params = {"source": collection}
        data = {"pipeline": pipeline}
        response = self._session.post(url, params=params, data=data)
        response.raise_for_status()
        return response.json()

    def get_db_size_gb(self) -> float:
        # GET /datalake/db-size/
        url = self._base_url / f"{self._PREFIX}/db-size/"
        response = self._session.get(url)
        response.raise_for_status()
        return response.json()

    def create_index(self, collection: str, index: list) -> None:
        # POST /datalake/index/
        url = self._base_url / f"{self._PREFIX}/index/"
        data = {"source": collection, "index": index}
        response = self._session.post(url, json=data)
        response.raise_for_status()
