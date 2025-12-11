from typing import Any

from splight_lib.client.datalake.common.abstract import AbstractDatalakeClient
from splight_lib.client.datalake.v4.remote_client import (
    BufferedAsyncRemoteDatalakeClient,
    BufferedSyncRemoteDataClient,
    SyncRemoteDatalakeClient,
)
from splight_lib.settings import (
    DatalakeClientType,
    SplightAPIVersion,
    datalake_settings,
    workspace_settings,
)

DL_CLIENT_TYPE_MAP = {
    DatalakeClientType.BUFFERED_ASYNC: BufferedAsyncRemoteDatalakeClient,
    DatalakeClientType.BUFFERED_SYNC: BufferedSyncRemoteDataClient,
    DatalakeClientType.SYNC: SyncRemoteDatalakeClient,
}


class DatalakeClientBuilder:
    @staticmethod
    def build(
        dl_client_type: DatalakeClientType = DatalakeClientType.BUFFERED_ASYNC,
        parameters: dict[str, Any] = {},
    ) -> AbstractDatalakeClient:
        return DL_CLIENT_TYPE_MAP[dl_client_type](**parameters)


def get_datalake_client() -> AbstractDatalakeClient:
    return DatalakeClientBuilder.build(
        dl_client_type=datalake_settings.DL_CLIENT_TYPE,
        parameters={
            "base_url": workspace_settings.SPLIGHT_PLATFORM_API_HOST,
            "access_id": workspace_settings.SPLIGHT_ACCESS_ID,
            "secret_key": workspace_settings.SPLIGHT_SECRET_KEY,
            "api_version": SplightAPIVersion.V4,
            "buffer_size": datalake_settings.DL_BUFFER_SIZE,
            "buffer_timeout": datalake_settings.DL_BUFFER_TIMEOUT,
        },
    )
