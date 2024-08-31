from datetime import datetime
from threading import Lock, Thread
from time import sleep
from typing import Any, TypedDict

import pandas as pd
from furl import furl
from retry import retry

from splight_lib.auth import SplightAuthToken
from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.client.datalake.buffer import DatalakeDocumentBuffer
from splight_lib.client.datalake.exceptions import DatalakeRequestError
from splight_lib.client.exceptions import SPLIGHT_REQUEST_EXCEPTIONS
from splight_lib.constants import (
    DEFAULT_COLLECTION,
    DEFAULT_SORT_FIELD,
    DL_BUFFER_SIZE,
    DL_BUFFER_TIMEOUT,
)
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.restclient import SplightRestClient

logger = get_splight_logger()


class Records(TypedDict):
    collection: str
    records: list[dict[str, Any]]


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
    def save(self, records: Records) -> list[dict]:
        url = self._base_url / f"{self._PREFIX}/write"
        response = self._restclient.post(url, json=records)
        if response.is_error:
            raise DatalakeRequestError(response.status_code, response.text)
        return records["records"]

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    async def async_save(
        self,
        records: Records,
    ) -> list[dict]:
        # POST /data/write
        url = self._base_url / f"{self._PREFIX}/write"
        response = await self._restclient.async_post(url, json=records)
        if response.is_error:
            raise DatalakeRequestError(response.status_code, response.text)
        return records["records"]

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _get(self, request: dict) -> list[dict]:
        url = self._base_url / f"{self._PREFIX}/read"
        response = self._restclient.post(url, json=request)
        if response.is_error:
            raise DatalakeRequestError(response.status_code, response.text)
        return response.json()

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    async def _async_get(self, request: dict) -> list[dict]:
        url = self._base_url / f"{self._PREFIX}/read"
        response = await self._restclient.async_post(url, json=request)
        if response.is_error:
            raise DatalakeRequestError(response.status_code, response.text)
        return response.json()

    def save_dataframe(
        self, dataframe: pd.DataFrame, collection: str = DEFAULT_COLLECTION
    ) -> None:
        dataframe = _fix_dataframe_timestamp(dataframe)
        instances = dataframe.to_dict("records")
        self.save({"collection": collection, "records": instances})

    def get_dataframe(
        self,
        match: dict[str, str],
        collection: str = DEFAULT_COLLECTION,
        sort_field: str = DEFAULT_SORT_FIELD,
        sort_direction: int = -1,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        extra_pipeline: list[dict] = [],
        aggregation_query: dict = {},
        limit: int = 10000,
        max_time_ms: int = 10000,
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

    def save(self, records: Records) -> list[dict]:
        logger.debug("Saving documents in datalake", tags=LogTags.DATALAKE)
        collection = records["collection"]
        instances = records["records"]
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
        logger.debug("Saving dataframe in datalake", tags=LogTags.DATALAKE)
        dataframe = _fix_dataframe_timestamp(dataframe)
        instances = dataframe.to_dict("records")
        self.save({"collection": collection, "records": instances})

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
    def _send_documents(self, collection: str, docs: list[dict]) -> list[dict]:
        url = self._base_url / f"{self._PREFIX}/write"
        data = {
            "collection": collection,
            "records": docs,
        }
        response = self._restclient.post(url, json=data)
        if response.is_error:
            raise DatalakeRequestError(response.status_code, response.text)
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
            tags=LogTags.DATALAKE,
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

    def save(self, records: Records) -> list[dict]:
        logger.debug("Saving documents in datalake", tag=LogTags.DATALAKE)
        collection = records["collection"]
        buffer = self._data_buffers[collection]
        with self._lock:
            buffer.add_documents(records["records"])
            if buffer.should_flush():
                logger.debug(
                    "Flushing datalake buffer with %s elements",
                    len(buffer.data),
                    tags=LogTags.DATALAKE,
                )
                self._send_documents(collection, buffer.data)
                buffer.reset()
        return records["records"]

    def save_dataframe(
        self, dataframe: pd.DataFrame, collection: str = DEFAULT_COLLECTION
    ) -> None:
        logger.debug("Saving dataframe in datalake", tag=LogTags.DATALAKE)
        # dataframe["timestamp"] = dataframe["timestamp"].apply(
        #     lambda x: x.tz_localize(tz="UTC").isoformat()
        # )
        dataframe = _fix_dataframe_timestamp(dataframe)
        instances = dataframe.to_dict("records")
        self.save(collection, instances)

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _send_documents(self, collection: str, docs: list[dict]) -> list[dict]:
        url = self._base_url / f"{self._PREFIX}/write"
        data = {
            "collection": collection,
            "records": docs,
        }
        response = self._restclient.post(url, json=data)
        if response.is_error:
            raise DatalakeRequestError(response.status_code, response.text)
        return docs


def _fix_dataframe_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    if df["timestamp"][0].tz is None:
        df["timestamp"] = df["timestamp"].apply(
            lambda x: x.tz_localize(tz="UTC").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
    else:
        df["timestamp"] = df["timestamp"].apply(
            lambda x: x.tz_convert(tz="UTC").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
    return df
