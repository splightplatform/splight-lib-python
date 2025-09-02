from typing import Any

from splight_lib.client.datalake.common.abstract import AbstractDatalakeClient
from splight_lib.client.datalake.v3.builder import (
    DatalakeClientBuilder as V3DatalakeClientBuilder,
)
from splight_lib.client.datalake.v4.builder import (
    DatalakeClientBuilder as V4DatalakeClientBuilder,
)
from splight_lib.settings import DatalakeClientType, SplightAPIVersion


class DatalakeClientBuilder:
    @staticmethod
    def build(
        version: SplightAPIVersion = SplightAPIVersion.V3,
        dl_client_type: DatalakeClientType = DatalakeClientType.BUFFERED_ASYNC,
        parameters: dict[str, Any] = {},
    ) -> AbstractDatalakeClient:
        if version == SplightAPIVersion.V3:
            builder = V3DatalakeClientBuilder
        elif version == SplightAPIVersion.V4:
            builder = V4DatalakeClientBuilder
        else:
            raise ValueError(f"Unsupported API version: {version}")

        return builder.build(dl_client_type, parameters)
