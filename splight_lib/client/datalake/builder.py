from typing import Any, Dict

from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.client.datalake.remote_client import (
    BufferedAsyncRemoteDatalakeClient,
    BufferedSyncRemoteDataClient,
    SyncRemoteDatalakeClient,
)
from splight_lib.settings import DatalakeClientType

DL_CLIENT_TYPE_MAP = {
    DatalakeClientType.BUFFERED_ASYNC: BufferedAsyncRemoteDatalakeClient,
    DatalakeClientType.BUFFERED_SYNC: BufferedSyncRemoteDataClient,
    DatalakeClientType.SYNC: SyncRemoteDatalakeClient,
}


class DatalakeClientBuilder:
    @staticmethod
    def build(
        dl_client_type: DatalakeClientType = DatalakeClientType.BUFFERED_ASYNC,
        parameters: Dict[str, Any] = {},
    ) -> AbstractDatalakeClient:
        return DL_CLIENT_TYPE_MAP[dl_client_type](**parameters)
