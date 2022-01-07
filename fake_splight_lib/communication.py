import time
import logging
from splight_communication.abstract import AbstractCommunication


class FakeQueueCommunication(AbstractCommunication):
    logger = logging.getLogger()

    def send(self, data: dict):
        self.logger.info(f"FakeQueueCommunication Sent data: {data}")

    def receive(self) -> dict:
        time.sleep(2)
        data = {"action": 'write', "variables": []}
        self.logger.info(f"FakeQueueCommunication Read data: {data}")
        return data
