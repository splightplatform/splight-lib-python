import re
import sys
from subprocess import Popen
from typing import Generator, Optional
from queue import Queue, Empty
from threading import Thread

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
        self._thread = None
        self._queue = None
        self._running = False

    def start(self):
        self._thread = Thread(target=self._consume_logs, daemon=True)
        self._queue = Queue()
        self._running = True
        self._thread.start()
        self._run()

    def stop(self):
        # self._process.kill()
        self._running = False
        self._thread.join(timeout=10)
        self._queue = None
        self._thread = None

    def _run(self):
        # for msg in self.logs_iterator():
        #     msg = msg.rstrip()
        #     print(msg)
        while True:
            try:
                self._client.stream_logs(self.logs_iterator, self._component_id)
            except Exception:
                print("Stream Stopped")
                break

    def _consume_logs(self):
        reader = iter(self._process.stdout.readline, "")
        for new_line in reader:
            if self._process.poll() is not None:
                # msg = "".join(self._message_buffer)
                # sys.stdout.write(msg)
                # yield msg
                output, error = self._process.communicate()
                output_msg = output.decode("utf-8")
                error_msg = error.decode("utf-8")
                # sys.stdout.write(output_msg)
                self._queue.put(output_msg)
                # sys.stdout.write(error_msg)
                self._queue.put(error_msg)
                break
            self._queue.put(new_line.decode("utf-8"))

    # def _restart(self):
    #     print("Restarting")
    #     self.stop()
    #     self.start()

    def logs_iterator(self) -> Generator:
        self._message_buffer = []
        while self._running:
            try:
                message = self._queue.get(timeout=10)
                # message = self._queue.get()
            except Empty:
                msg = "".join(self._message_buffer)
                if msg:
                    sys.stdout.write(msg)
                    yield msg
                # self._restart()
                return
                # break

            # yield message
            full_msg = self._generate_message(message)
            if not full_msg:
                continue
            yield full_msg
            sys.stdout.write(full_msg)
        # reader = iter(self._process.stdout.readline, "")
        # for new_line in reader:
        #     if self._process.poll() is not None:
        #         msg = "".join(self._message_buffer)
        #         sys.stdout.write(msg)
        #         yield msg
        #         output, error = self._process.communicate()
        #         output_msg = output.decode("utf-8")
        #         error_msg = error.decode("utf-8")
        #         sys.stdout.write(output_msg)
        #         yield output_msg
        #         sys.stdout.write(error_msg)
        #         yield error_msg
        #         break
        #
        #     line_msg = new_line.decode("utf-8")
        #     sys.stdout.write(line_msg)
        #
        #     full_msg = self._generate_message(line_msg)
        #     if not full_msg:
        #         continue
        #     yield full_msg

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