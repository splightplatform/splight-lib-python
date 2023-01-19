from datetime import timedelta, timezone
from io import StringIO
from tempfile import NamedTemporaryFile
from typing import Dict, List, Union

import pandas as pd
import json
from furl import furl
from pydantic import BaseModel
from requests import Session

from remote_splight_lib.auth import SplightAuthToken
from remote_splight_lib.settings import settings
from splight_abstract import AbstractRemoteClient, QuerySet
from splight_abstract.datalake import AbstractDatalakeClient, validate_resource_type, validate_instance_type
from splight_models import Query, DatalakeModel
from retry import retry

from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
)
REQUEST_EXCEPTIONS = (ConnectionError, Timeout, HTTPError)


class DatalakeClient(AbstractDatalakeClient, AbstractRemoteClient):

    _PREFIX = "v2/engine/datalake"

    def __init__(self, namespace: str = "default"):
        super(DatalakeClient, self).__init__(namespace=namespace)
        self._base_url = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._session = Session()
        self._session.headers.update(token.header)

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _raw_save(
        self,
        collection: str,
        instances: List[DatalakeModel],
    ) -> List[DatalakeModel]:
        url = self._base_url / f"{self._PREFIX}/save/"
        data = [json.loads(model.json()) for model in instances]
        response = self._session.post(
            url, params={"source": collection}, json=data
        )
        response.raise_for_status()
        return instances

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _raw_get(
        self,
        resource_type: DatalakeModel,
        collection: str, 
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
                # "tzinfo": tzinfo
            }
        )
        if group_id:
            valid_kwargs.update({"group_id": group_id})
        if group_fields:
            valid_kwargs.update({"group_fields": group_fields})
        params = self._parse_params(**valid_kwargs)
        response = self._session.get(url, params=params)
        response.raise_for_status()
        output = [
            resource_type.parse_obj(item)
            for item in response.json()["results"]
        ]
        return output

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _raw_delete(self, collection: DatalakeModel, **kwargs) -> None:
        # DELETE /datalake/delete/
        url = self._base_url / f"{self._PREFIX}/delete/"
        params = {"source": collection}
        response = self._session.delete(url, params=params, json=kwargs)
        response.raise_for_status()

    @validate_resource_type
    def get(
        self,
        resource_type: DatalakeModel,
        *args,
        **kwargs,
    ) -> List[BaseModel]:
        kwargs["get_func"] = "_raw_get"
        kwargs["count_func"] = "None"
        kwargs["collection"] = resource_type.Meta.collection_name
        return QuerySet(self, *args, **kwargs)

    def get_output(self, query: Query) -> List[Dict]:
        # TODO: Add add_fields, project and renaming
        return self._raw_get(
            collection=query.source,
            limit_=query.limit,
            skip_=query.skip,
            sort=query.sort,
            group_id=query.group_id,
            group_fields=query.group_fields,
            tzinfo=timezone(timedelta(hours=query.timezone_offset)),
            **query.filters
        )

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    @validate_resource_type
    def get_dataframe(self, resource_type: DatalakeModel, **kwargs) -> pd.DataFrame:
        # GET /datalake/dumpdata/?source=collection
        url = self._base_url / f"{self._PREFIX}/dumpdata/"
        collection = resource_type.Meta.collection_name
        kwargs.update({"source": collection})
        params = self._parse_params(**kwargs)
        response = self._session.get(url, params=params)
        response.raise_for_status()

        df: pd.DataFrame = pd.DataFrame(pd.read_csv(StringIO(response.text)))
        if df.empty:
            return df
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        return df

    def get_dataset(self, queries: List[Dict]) -> pd.DataFrame:
        # TODO this should be 
        # def get_dataset(self, queries: List[Query]) -> pd.DataFrame:
        dfs = [self.get_dataframe(**query) for query in queries]
        df = pd.concat(dfs, axis=1)
        return df

    @validate_instance_type
    def save(
        self,
        instances: List[DatalakeModel],
    ) -> List[DatalakeModel]:
        # POST /datalake/save/
        if not instances:
            return instances
        resource_type = instances[0].__class__
        collection = resource_type.Meta.collection_name
        return self._raw_save(collection=collection, instances=instances)

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    @validate_resource_type
    def save_dataframe(self, resource_type: DatalakeModel, dataframe: pd.DataFrame) -> None:
        # POST /datalake/loaddata/
        url = self._base_url / f"{self._PREFIX}/loaddata/"

        tmp_file = NamedTemporaryFile("w")
        with open(tmp_file.name, "wb") as fid:
            dataframe.to_csv(fid)
        collection = resource_type.Meta.collection_name
        response = self._session.post(
            url,
            data={"source": collection},
            files={"file": open(tmp_file.name)},
        )
        response.raise_for_status()

    @validate_resource_type
    def delete(self, resource_type: DatalakeModel, **kwargs) -> None:
        collection = resource_type.Meta.collection_name
        return self._raw_delete(collection=collection, **kwargs)

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def create_index(self, collection: str, index: list) -> None:
        # POST /datalake/index/
        url = self._base_url / f"{self._PREFIX}/index/"
        data = {"source": collection, "index": index}
        response = self._session.post(url, json=data)
        response.raise_for_status()

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
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
