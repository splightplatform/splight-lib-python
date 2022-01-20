import logging
from splight_communication.abstract import AbstractCommunication


from queue import Queue
import json

QUEUE = Queue()


class FakeQueueCommunication(AbstractCommunication):
    logger = logging.getLogger()

    def __init__(self, *args, **kwargs):
        pass

    def send(self, data: dict) -> None:
        self.logger.debug(f"FakeQueueCommunication Sent data: {data}")
        QUEUE.put(json.dumps(data))

    def receive(self) -> dict:
        data = json.loads(QUEUE.get())
        self.logger.debug(f"FakeQueueCommunication Read data: {data}")
        return data
