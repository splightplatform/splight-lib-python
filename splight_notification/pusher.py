from pusher import Pusher
from .abstract import AbstractNotificationClient
from .settings import PUSHER_CONFIG
from typing import Dict


class PusherClient(AbstractNotificationClient):
    def __init__(self, channel: str):
        self._channel = channel
        self._client = Pusher(**PUSHER_CONFIG)

    def send(self, topic: str, data: Dict):
        self._client.trigger(self._channel, topic, data)

    def authenticate(self, socket: str) -> Dict:
        return self._client.authenticate(self._channel, socket)
