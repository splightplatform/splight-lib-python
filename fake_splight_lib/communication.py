import time
import logging
from splight_communication.abstract import AbstractCommunication


class FakeQueueCommunication(AbstractCommunication):
    logger = logging.getLogger()

    def send(self, data: dict):
        self.logger.info(f"Data sent: {data}")

    def receive(self) -> dict:
        time.sleep(2)
        self.logger.info(f"Data read")
        return {"action": 'write', "variables": []}
