import logging
from splight_communication.abstract import AbstractCommunication
from datetime import date, datetime


from queue import Queue
import json

QUEUE = Queue()
logger = logging.getLogger()


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

class FakeQueueCommunication(AbstractCommunication):

    def __init__(self, *args, **kwargs):
        self.topic = "default"

    def send(self, data: dict) -> None:
        logger.debug(f"FakeQueueCommunication Sent data: {data}")
        QUEUE.put(json.dumps(data, default=json_serial))

    def receive(self) -> dict:
        data = json.loads(QUEUE.get())
        logger.debug(f"FakeQueueCommunication Read data: {data}")
        return data

    @staticmethod
    def create_topic(topic: str) -> None:
        logger.debug(f"FakeQueueCommunication Created topic: {topic}")
