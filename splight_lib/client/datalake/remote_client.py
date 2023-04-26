import json
from datetime import timedelta, timezone
from io import StringIO
from tempfile import NamedTemporaryFile
from typing import Dict, List, Union

import pandas as pd
from furl import furl
from pydantic import BaseModel
from remote_splight_lib.auth import SplightAuthToken
from retry import retry
from splight_abstract import AbstractRemoteClient, QuerySet
from splight_abstract.datalake import (
    AbstractDatalakeClient,
    validate_datalake_instance_type,
    validate_datalake_resource_type,
)
from splight_lib.client.exceptions import SPLIGHT_REQUEST_EXCEPTIONS
from splight_lib.client.settings import settings_remote as settings
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.restclient import SplightRestClient
from splight_models import DatalakeModel, Query

logger = get_splight_logger()


class RemoteDatalakeClient(AbstractDatalakeClient, AbstractRemoteClient):
    _PREFIX = "v2/engine/datalake"

    def __init__(self, namespace: str = "default", *args, **kwargs):
        super().__init__(namespace=namespace)
        self._base_url = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._restclient = SplightRestClient()
        self._restclient.update_headers(token.header)
        logger.info(
            "Remote datalake client initialized.", tags=LogTags.DATALAKE
        )

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _raw_save(
        self,
        collection: str,
        instances: List[DatalakeModel],
    ) -> List[DatalakeModel]:
        url = self._base_url / f"{self._PREFIX}/save/"
        data = [json.loads(model.json()) for model in instances]
        response = self._restclient.post(
            url, params={"source": collection}, json=data
        )
        response.raise_for_status()
        return instances

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
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
        response = self._restclient.get(url, params=params)
        response.raise_for_status()
        output = [
            resource_type.parse_obj(item)
            for item in response.json()["results"]
        ]
        return output

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _raw_delete(self, collection: str, **kwargs) -> None:
        # DELETE /datalake/delete/
        url = self._base_url / f"{self._PREFIX}/delete/"
        params = {"source": collection}
        response = self._restclient.delete(url, params=params, json=kwargs)
        response.raise_for_status()

    @validate_datalake_resource_type
    def get(
        self,
        resource_type: DatalakeModel,
        *args,
        **kwargs,
    ) -> List[BaseModel]:
        logger.debug(
            "Retrieving object of type %s from datalake.",
            resource_type,
            tags=LogTags.DATALAKE,
        )
        kwargs["get_func"] = "_raw_get"
        kwargs["count_func"] = "None"
        kwargs["collection"] = resource_type.Meta.collection_name
        kwargs["resource_type"] = resource_type
        return QuerySet(self, *args, **kwargs)

    def get_output(
        self, resource_type: DatalakeModel, query: Query
    ) -> List[Dict]:
        # TODO: Add add_fields, project and renaming
        logger.debug(
            "Retrieving output of type %s from datalake.",
            resource_type,
            tags=LogTags.DATALAKE,
        )
        return self._raw_get(
            resource_type=resource_type,
            collection=query.source,
            limit_=query.limit,
            skip_=query.skip,
            sort=query.sort,
            group_id=query.group_id,
            group_fields=query.group_fields,
            tzinfo=timezone(timedelta(hours=query.timezone_offset)),
            **query.filters,
        )

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    @validate_datalake_resource_type
    def get_dataframe(
        self, resource_type: DatalakeModel, **kwargs
    ) -> pd.DataFrame:
        # Add this parameter to the request in order to make
        # the Mongo query work faster.
        # It should be the same as the resource_type.
        if "output_format" not in kwargs:
            kwargs["output_format"] = resource_type.class_name()

        # GET /datalake/dumpdata/?source=collection
        url = self._base_url / f"{self._PREFIX}/dumpdata/"
        collection = resource_type.Meta.collection_name
        kwargs.update({"source": collection})
        params = self._parse_params(**kwargs)
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

    def get_dataset(
        self, resource_type: DatalakeModel, queries: List[Dict]
    ) -> pd.DataFrame:
        logger.debug(
            "Retrieving dataset from datalake.", tags=LogTags.DATALAKE
        )

        dfs = [
            self.get_dataframe(resource_type=resource_type, **query)
            for query in queries
        ]
        if dfs:
            return pd.concat(dfs, axis=1)
        return pd.DataFrame(dfs)

    @validate_datalake_instance_type
    def save(
        self,
        instances: List[DatalakeModel],
    ) -> List[DatalakeModel]:
        # POST /datalake/save/
        logger.debug("Saving instances %s.", instances, tags=LogTags.DATALAKE)

        if not instances:
            return instances
        resource_type = instances[0].__class__
        collection = resource_type.Meta.collection_name
        return self._raw_save(collection=collection, instances=instances)

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    @validate_datalake_resource_type
    def save_dataframe(
        self, resource_type: DatalakeModel, dataframe: pd.DataFrame
    ) -> None:
        logger.debug("Saving dataframe.", tags=LogTags.DATALAKE)

        # POST /datalake/loaddata/
        url = self._base_url / f"{self._PREFIX}/loaddata/"

        tmp_file = NamedTemporaryFile("w")
        with open(tmp_file.name, "wb") as fid:
            dataframe.to_csv(fid)
        collection = resource_type.Meta.collection_name
        response = self._restclient.post(
            url,
            data={"source": collection},
            files={"file": open(tmp_file.name, mode="rb")},
        )
        response.raise_for_status()

    @validate_datalake_resource_type
    def delete(self, resource_type: DatalakeModel, **kwargs) -> None:
        logger.debug(
            "Deleting resources of type %s from datalake.",
            resource_type,
            tags=LogTags.DATALAKE,
        )

        collection = resource_type.Meta.collection_name
        return self._raw_delete(collection=collection, **kwargs)

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
