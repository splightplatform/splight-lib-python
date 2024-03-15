from typing import Any, Dict

from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.client.datalake.local_client import LocalDatalakeClient
from splight_lib.client.datalake.remote_client import (
    BufferedAsyncRemoteDatalakeClient,
    BufferedSyncRemoteDataClient,
    SyncRemoteDatalakeClient,
)
from splight_lib.constants import DL_CLIENT_ALLOWED_TYPES

dl_client_type_map = {
    "buffered_async": BufferedAsyncRemoteDatalakeClient,
    "buffered_sync": BufferedSyncRemoteDataClient,
    "sync": SyncRemoteDatalakeClient,
    "local": LocalDatalakeClient,
}


class DatalakeClientBuilder:
    @staticmethod
    def build(
        dl_client_type: str = "buffered_sync",
        parameters: Dict[str, Any] = {},
    ) -> AbstractDatalakeClient:
        if not dl_client_type in DL_CLIENT_ALLOWED_TYPES:
            raise ValueError(
                "Expected value in %s. Got %s",
                DL_CLIENT_ALLOWED_TYPES,
                dl_client_type,
            )
        return dl_client_type_map[dl_client_type](**parameters)
