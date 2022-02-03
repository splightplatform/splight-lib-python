import logging
from splight_notification.abstract import AbstractNotificationClient
from typing import Dict


class FakeNotificationClient(AbstractNotificationClient):
    logger = logging.getLogger()

    def __init__(self, channel: str):
        self.channel_name = 'fake_notification_channel'

    def authenticate(self, socket: str) -> Dict:
        return {"auth": "abc123"}

    def send(self, topic: str, data: Dict) -> None:
        self.logger.debug(f"{__class__.__name__} Sent data: {data} {topic}")
