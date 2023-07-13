import re
import sys
from subprocess import Popen
from typing import Generator, Optional

from splight_lib.client.grpc.client import LogsGRPCClient
from splight_lib.settings import settings

LOG_FORMAT = r"^.* \| .* \| .*:\d{2,} \| .* "
LOG_PATTERN = re.compile(LOG_FORMAT)


class ComponentLogsStreamer:
    def __init__(self, process: Popen, component_id: str):
        self._process = process
        self._component_id = component_id

        self._client = LogsGRPCClient(
            grpc_host=settings.SPLIGHT_GRPC_HOST, secure_channel=True
        )
        self._client.set_authorization_header(
            access_id=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._logs_entry = self._client._log_entry

    def start(self):
        self._run()

    def stop(self):
        self._thread.stop()

    def _run(self):
        self._client.stream_logs(self.logs_iterator, self._component_id)

    def logs_iterator(self) -> Generator:
        self._message_buffer = []
        reader = iter(self._process.stdout.readline, "")
        for new_line in reader:
            if self._process.poll() is not None:
                msg = "".join(self._message_buffer)
                sys.stdout.write(msg)
                yield msg
                output, error = self._process.communicate()
                output_msg = output.decode("utf-8")
                error_msg = error.decode("utf-8")
                sys.stdout.write(output_msg)
                yield output_msg
                sys.stdout.write(error_msg)
                yield error_msg
                break

            line_msg = new_line.decode("utf-8")
            sys.stdout.write(line_msg)

            full_msg = self._generate_message(line_msg)
            if not full_msg:
                continue
            yield full_msg

    def _generate_message(self, raw_msg: str) -> Optional[str]:
        if self._is_log(raw_msg):
            msg = "".join(self._message_buffer)
            self._message_buffer = [raw_msg]
            return msg
        self._message_buffer.append(raw_msg)
        return None

    def _is_log(self, raw_msg: str) -> bool:
        match = LOG_PATTERN.match(raw_msg)
        return True if match else False
