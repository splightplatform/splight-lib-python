import re
import sys
from queue import Empty, Queue
from subprocess import Popen
from threading import Thread
from typing import Generator, Optional

from splight_lib.client.grpc.client import LogsGRPCClient, LogsGRPCError
from splight_lib.component.exceptions import LogsStreamerError
from splight_lib.settings import settings

LOG_FORMAT = r"^.* \| .* \| .*:\d{2,} \| .* "
LOG_PATTERN = re.compile(LOG_FORMAT)


class ComponentLogsStreamer:
    def __init__(self, process: Popen, component_id: str):
        self._process = process
        self._component_id = component_id

        try:
            self._client = self._create_client()
        except Exception as exc:
            raise LogsStreamerError(
                "Unable to connect to gRPC server"
            ) from exc
        self._logs_entry = self._client._log_entry
        self._thread: Optional[Thread] = None
        self._queue: Optional[Queue] = None
        self._running: bool = False

    def _create_client(self):
        client = LogsGRPCClient(
            grpc_host=settings.SPLIGHT_GRPC_HOST, secure_channel=True
        )
        client.set_authorization_header(
            access_id=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        return client

    def start(self):
        self._thread = Thread(target=self._consume_logs, daemon=True)
        self._queue = Queue()
        self._running = True
        self._thread.start()
        self._run()

    def stop(self):
        self._running = False
        self._thread.join(timeout=10)
        self._queue = None
        self._thread = None

    def _run(self):
        while self._running:
            try:
                self._client.stream_logs(
                    self.logs_iterator, self._component_id
                )
            except LogsGRPCError as exc:
                raise LogsStreamerError(
                    "Component Logs stream stopped"
                ) from exc

    def _consume_logs(self):
        reader = iter(self._process.stdout.readline, "")
        for new_line in reader:
            if self._process.poll() is not None:
                output, error = self._process.communicate()
                output_msg = output.decode("utf-8")
                error_msg = error.decode("utf-8")
                self._queue.put(output_msg)
                self._queue.put(error_msg)
                self._running = False
                break
            self._queue.put(new_line.decode("utf-8"))

    def logs_iterator(self) -> Generator:
        self._message_buffer = []
        while True:
            try:
                message = self._queue.get(timeout=10)
            except Empty:
                msg = "".join(self._message_buffer)
                if msg:
                    sys.stdout.write(msg)
                    yield msg
                return

            full_msg = self._generate_message(message)
            if not full_msg:
                continue
            yield full_msg
            sys.stdout.write(full_msg)

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
