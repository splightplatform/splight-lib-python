from typing import Any, Dict

from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.client.datalake.local_client import LocalDatalakeClient
from splight_lib.client.datalake.remote_client import RemoteDatalakeClient


class DatalakeClientBuilder:
    @staticmethod
    def build(
        local: bool = False, parameters: Dict[str, Any] = {}
    ) -> AbstractDatalakeClient:
        if local:
            dl_client = LocalDatalakeClient(**parameters)
        else:
            dl_client = RemoteDatalakeClient(**parameters)
        return dl_client
