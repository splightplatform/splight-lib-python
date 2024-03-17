from typing import Any, Dict

from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.client.datalake.local_client import LocalDatalakeClient
from splight_lib.client.datalake.remote_client import (
    BufferedAsyncRemoteDatalakeClient,
    BufferedSyncRemoteDataClient,
    SyncRemoteDatalakeClient,
)
from splight_lib.settings import DatalakeClientType

DL_CLIENT_TYPE_MAP = {
    "buffered_async": BufferedAsyncRemoteDatalakeClient,
    "buffered_sync": BufferedSyncRemoteDataClient,
    "sync": SyncRemoteDatalakeClient,
    "local": LocalDatalakeClient,
}


class DatalakeClientBuilder:
    @staticmethod
    def build(
        dl_client_type: DatalakeClientType = DatalakeClientType.BUFFERED_ASYNC,
        parameters: Dict[str, Any] = {},
    ) -> AbstractDatalakeClient:
        if not dl_client_type in set(DatalakeClientType):
            raise ValueError(
                "Value '%s' is not one of the available buffers: %s",
                dl_client_type,
                set(DatalakeClientType),
            )
        return DL_CLIENT_TYPE_MAP[dl_client_type](**parameters)
