import logging
from splight_communication.abstract import AbstractCommunication
from datetime import date, datetime


from queue import Queue
import json

QUEUE = Queue()


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

class FakeQueueCommunication(AbstractCommunication):
    logger = logging.getLogger()

    def __init__(self, *args, **kwargs):
        self.topic = "default"

    def send(self, data: dict) -> None:
        self.logger.debug(f"FakeQueueCommunication Sent data: {data}")
        QUEUE.put(json.dumps(data, default=json_serial))

    def receive(self) -> dict:
        data = json.loads(QUEUE.get())
        self.logger.debug(f"FakeQueueCommunication Read data: {data}")
        return data
