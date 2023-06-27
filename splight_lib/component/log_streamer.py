from typing import Generator
from subprocess import Popen

from splight_lib.client.grpc.client import LogsGRPCClient
from splight_lib.settings import settings


class ComponentLogsStreamer:
    def __init__(self, process: Popen, component_id: str):
        self._process = process
        self._component_id = component_id

        self._client = LogsGRPCClient(
            grpc_host=settings.SPLIGHT_GRPC_HOST,
        )
        self._client.set_authorization_header(
            access_id=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._logs_entry = self._client._log_entry

    def start(self):
        self._client.stream_logs(self.logs_iterator, self._component_id)

    def logs_iterator(self) -> Generator:
        while True:
            new_line = self._process.stdout.readline()
            message = new_line.rstrip()
            print(message)
            yield message
