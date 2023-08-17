from typing import Callable, Optional, Tuple

import grpc

from splight_lib.client.grpc.decorators import retry_streaming
from splight_lib.client.grpc.reflector import GrpcReflectionClient


class LogsGRPCError(Exception):
    pass


class MissingGRPCService(Exception):
    pass


class SplightGRPCClient:
    AUTHORIZATION: str = "authorization"
    _SERVICE_NAME: str = None

    def __init__(self, grpc_host: str, secure_channel: bool = True):
        if not self._SERVICE_NAME:
            raise MissingGRPCService("Missing parameter service_name")

        if secure_channel:
            self._channel = grpc.secure_channel(
                grpc_host, grpc.ssl_channel_credentials()
            )
        else:
            self._channel = grpc.insecure_channel(grpc_host)

        self._reflector = GrpcReflectionClient()
        self._reflector.load_protocols(
            self._channel, symbols=[self._SERVICE_NAME]
        )
        self._stub = self._reflector.service_stub_class(self._SERVICE_NAME)(
            self._channel
        )
        self._auth_header: Optional[Tuple[str, str]] = None

    def set_authorization_header(self, access_id: str, secret_key: str):
        self._auth_header = (
            SplightGRPCClient.AUTHORIZATION,
            f"Splight {access_id} {secret_key}",
        )


class LogsGRPCClient(SplightGRPCClient):
    _SERVICE_NAME: str = "LogsService"
    _LOG_ENTRY: str = "LogEntry"

    def __init__(self, grpc_host: str, secure_channel: bool = True):
        super().__init__(grpc_host, secure_channel=secure_channel)
        self._log_entry = self._reflector.message_class(self._LOG_ENTRY)

    @retry_streaming(times=5)
    def stream_logs(self, log_generator: Callable, component_id: str):
        try:
            self._stub.stash_log_entry(
                self._parse_log_message(log_generator(), component_id),
                metadata=[self._auth_header],
            )
        except grpc.RpcError as exc:
            raise LogsGRPCError("Unable to stream component logs") from exc

    def _parse_log_message(self, message_iterator: str, component_id: str):
        for message in message_iterator:
            yield self._log_entry(
                message=message,
                component_id=component_id,
            )
