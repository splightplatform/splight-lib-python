from datetime import datetime
from threading import Lock, Thread
from time import sleep
from typing import Dict, List, Optional, Union

import pandas as pd
from furl import furl
from retry import retry

from splight_lib.auth import SplightAuthToken
from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.client.datalake.buffer import DatalakeDocumentBuffer
from splight_lib.client.datalake.exceptions import InvalidCollectionName
from splight_lib.client.datalake.schemas import DataRequest
from splight_lib.client.exceptions import SPLIGHT_REQUEST_EXCEPTIONS
from splight_lib.constants import (
    DEFAULT_COLLECTION,
    DEFAULT_SORT_FIELD,
    DL_BUFFER_SIZE,
    DL_BUFFER_TIMEOUT,
)
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.restclient import SplightRestClient
from splight_lib.stringcase import camelcase

logger = get_splight_logger()


class SyncRemoteDatalakeClient(AbstractDatalakeClient):
    _PREFIX = "/data"

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
        # POST /data/write
        instances = instances if isinstance(instances, list) else [instances]
        url = self._base_url / f"{self._PREFIX}/write"
        collection = camelcase(collection)
        data = {
            "collection": collection,
            "records": instances,
        }
        response = self._restclient.post(url, json=data)
        response.raise_for_status()
        return instances

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    async def async_save(
        self,
        collection: str,
        instances: Union[List[Dict], Dict],
    ) -> List[dict]:
        # POST /data/write
        instances = instances if isinstance(instances, list) else [instances]
        url = self._base_url / f"{self._PREFIX}/write"
        data = {
            "collection": collection,
            "records": instances,
        }
        response = await self._restclient.async_post(url, json=data)
        response.raise_for_status()
        return instances

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _get(
        self,
        match: Dict[str, str],
        collection: str = DEFAULT_COLLECTION,
        sort_field: str = DEFAULT_SORT_FIELD,
        sort_direction: int = -1,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        extra_pipeline: List[Dict] = [],
        aggregation_query: Dict = {},
        limit: int = 10000,
        max_time_ms: Optional[int] = 10000,
    ) -> List[Dict]:
        # POST /data/read
        url = self._base_url / f"{self._PREFIX}/read"
        pipeline = [{"$match": match}, *extra_pipeline]
        data_request = DataRequest(
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            collection=collection,
            sort_field=sort_field,
            sort_direction=sort_direction,
            limit=limit,
            max_time_ms=max_time_ms,
            traces=[
                {
                    "ref_id": "output",
                    "type": "QUERY",
                    "pipeline": pipeline,
                    "expression": None,
                }
            ],
            aggregation_query=aggregation_query,
        )
        response = self._restclient.post(url, json=data_request.dict())
        response.raise_for_status()
        return response.json()

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    async def _async_get(
        self,
        match: Dict[str, str],
        collection: str = DEFAULT_COLLECTION,
        sort_field: str = DEFAULT_SORT_FIELD,
        sort_direction: int = -1,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        extra_pipeline: List[Dict] = [],
        aggregation_query: Dict = {},
        limit: int = 10000,
        max_time_ms: Optional[int] = 10000,
    ) -> List[Dict]:
        # POST /data/read
        url = self._base_url / f"{self._PREFIX}/read"
        pipeline = [{"$match": match}, *extra_pipeline]
        data_request = DataRequest(
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            collection=collection,
            sort_field=sort_field,
            sort_direction=sort_direction,
            limit=limit,
            max_time_ms=max_time_ms,
            traces=[
                {
                    "ref_id": "output",
                    "type": "QUERY",
                    "pipeline": pipeline,
                    "expression": None,
                }
            ],
            aggregation_query=aggregation_query,
        )
        response = await self._restclient.async_post(
            url, json=data_request.dict()
        )
        response.raise_for_status()
        return response.json()

    def save_dataframe(
        self, dataframe: pd.DataFrame, collection: str = DEFAULT_COLLECTION
    ) -> None:
        dataframe["timestamp"] = dataframe["timestamp"].apply(
            lambda x: x.tz_localize(tz="UTC").isoformat()
        )
        docs = dataframe.to_dict("records")
        self.save(collection, docs)

    def get_dataframe(
        self,
        match: Dict[str, str],
        collection: str = DEFAULT_COLLECTION,
        sort_field: str = DEFAULT_SORT_FIELD,
        sort_direction: int = -1,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        extra_pipeline: List[Dict] = [],
        aggregation_query: Dict = {},
        limit: int = 10000,
        max_time_ms: Optional[int] = 10000,
        **kwargs,
    ) -> pd.DataFrame:
        data = self._get(
            match,
            collection,
            sort_field,
            sort_direction,
            from_timestamp,
            to_timestamp,
            extra_pipeline,
            aggregation_query,
            limit,
            max_time_ms,
        )
        df = pd.DataFrame(data)
        if not df.empty:
            df.index = pd.to_datetime(df["timestamp"])
            df.drop(columns=["timestamp"], inplace=True)
            df.rename(columns={"output": "value"}, inplace=True)
            for key, value in match.items():
                df[key] = value
        return df


class BufferedAsyncRemoteDatalakeClient(SyncRemoteDatalakeClient):
    _PREFIX = "data"

    def __init__(
        self,
        base_url: str,
        access_id: str,
        secret_key: str,
        buffer_size: int = DL_BUFFER_SIZE,
        buffer_timeout: float = DL_BUFFER_TIMEOUT,
        *args,
        **kwargs,
    ):
        super().__init__(
            base_url,
            access_id,
            secret_key,
            buffer_size,
            buffer_timeout,
            *args,
            **kwargs,
        )
        self._base_url = furl(base_url)
        token = SplightAuthToken(
            access_key=access_id,
            secret_key=secret_key,
        )
        self._restclient = SplightRestClient()
        self._restclient.update_headers(token.header)

        logger.debug(
            "Initializing buffer with size %s and timeout %s",
            buffer_size,
            buffer_timeout,
        )
        self._data_buffers = {
            "default": DatalakeDocumentBuffer(buffer_size, buffer_timeout),
            "routine_evaluations": DatalakeDocumentBuffer(
                buffer_size, buffer_timeout
            ),
        }
        self._lock = Lock()
        self._flush_thread = Thread(target=self._flusher, daemon=True)
        self._flush_thread.start()
        logger.debug(
            "Buffered Remote datalake client initialized.",
            tags=LogTags.DATALAKE,
        )

    def save(
        self, collection: str, instances: Union[List[Dict], Dict]
    ) -> List[Dict]:
        logger.debug("Saving documents in datalake")
        instances = instances if isinstance(instances, List) else [instances]
        if collection not in self._data_buffers:
            raise InvalidCollectionName(collection)
        buffer = self._data_buffers[collection]
        with self._lock:
            if buffer.should_flush():
                logger.debug(
                    "Flushing datalake buffer with %s elements",
                    len(buffer.data),
                )
                self._send_documents(collection, buffer.data)
                buffer.reset()
            buffer.add_documents(instances)
        return instances

    def save_dataframe(
        self, dataframe: pd.DataFrame, collection: str = DEFAULT_COLLECTION
    ) -> None:
        logger.debug("Saving dataframe in datalake")
        dataframe["timestamp"] = dataframe["timestamp"].apply(
            lambda x: x.tz_localize(tz="UTC").isoformat()
        )
        instances = dataframe.to_dict("records")
        self.save(collection, instances)

    def _flusher(self):
        while True:
            for collection, buffer in self._data_buffers.items():
                self._flush_buffer(collection, buffer)
            sleep(0.5)

    def _flush_buffer(
        self, collection: str, buffer: DatalakeDocumentBuffer
    ) -> None:
        with self._lock:
            if buffer.should_flush():
                try:
                    logger.debug(
                        "Flushing datalake buffer with %s elements",
                        len(buffer.data),
                    )
                    self._send_documents(collection, buffer.data)
                    buffer.reset()
                except Exception:
                    logger.error("Unable to save documents", exc_info=True)

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _send_documents(self, collection: str, docs: List[Dict]) -> List[Dict]:
        url = self._base_url / f"{self._PREFIX}/write"
        collection = camelcase(collection)
        data = {
            "collection": collection,
            "records": docs,
        }
        response = self._restclient.post(url, json=data)
        response.raise_for_status()
        return docs


class BufferedSyncRemoteDataClient(SyncRemoteDatalakeClient):
    _PREFIX = "data"

    def __init__(
        self,
        base_url: str,
        access_id: str,
        secret_key: str,
        buffer_size: int = DL_BUFFER_SIZE,
        buffer_timeout: float = DL_BUFFER_TIMEOUT,
        *args,
        **kwargs,
    ):
        super().__init__(
            base_url,
            access_id,
            secret_key,
            buffer_size,
            buffer_timeout,
            *args,
            **kwargs,
        )
        self._base_url = furl(base_url)
        token = SplightAuthToken(
            access_key=access_id,
            secret_key=secret_key,
        )
        self._restclient = SplightRestClient()
        self._restclient.update_headers(token.header)

        logger.debug(
            "Initializing buffer with size %s and timeout %s",
            buffer_size,
            buffer_timeout,
        )
        self._data_buffers = {
            "default": DatalakeDocumentBuffer(buffer_size, buffer_timeout),
            "routine_evaluations": DatalakeDocumentBuffer(
                buffer_size, buffer_timeout
            ),
        }
        self._lock = Lock()
        logger.debug(
            "Synchronous Buffered Remote datalake client initialized.",
            tags=LogTags.DATALAKE,
        )

    def save(
        self, collection: str, instances: Union[List[Dict], Dict]
    ) -> List[Dict]:
        logger.debug("Saving documents in datalake")
        instances = instances if isinstance(instances, List) else [instances]
        if collection not in self._data_buffers:
            raise InvalidCollectionName(collection)
        buffer = self._data_buffers[collection]
        with self._lock:
            buffer.add_documents(instances)
            if buffer.should_flush():
                logger.debug(
                    "Flushing datalake buffer with %s elements",
                    len(buffer.data),
                )
                self._send_documents(collection, buffer.data)
                buffer.reset()
        return instances

    def save_dataframe(
        self, dataframe: pd.DataFrame, collection: str = DEFAULT_COLLECTION
    ) -> None:
        logger.debug("Saving dataframe in datalake")
        dataframe["timestamp"] = dataframe["timestamp"].apply(
            lambda x: x.tz_localize(tz="UTC").isoformat()
        )
        instances = dataframe.to_dict("records")
        self.save(collection, instances)

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _send_documents(self, collection: str, docs: List[Dict]) -> List[Dict]:
        url = self._base_url / f"{self._PREFIX}/write"
        collection = camelcase(collection)
        data = {
            "collection": collection,
            "records": docs,
        }
        response = self._restclient.post(url, json=data)
        response.raise_for_status()
        return docs
