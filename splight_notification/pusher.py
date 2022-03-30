from pusher import Pusher
from .abstract import AbstractNotificationClient
from splight_models import Channel
from .settings import PUSHER_CONFIG
from typing import Dict

class PusherClient(AbstractNotificationClient):

    def __init__(self, *args, **kwargs):
        super(PusherClient, self).__init__(*args, **kwargs)
        self._client = Pusher(**PUSHER_CONFIG)

    def get_channel_name(self, channel: str, channel_type: Channel) -> str:
        return f"{channel_type.value}-{self.namespace}-{channel}"

    def send(self, topic: str, data: Dict, channel: str = "default", channel_type: Channel = Channel.PRIVATE) -> None:
        channel = self.get_channel_name(channel, channel_type)
        self._client.trigger(channel, topic, data)

    def authenticate(self, socket: str, channel: str = "default", channel_type: Channel = Channel.PRIVATE) -> Dict:
        channel = self.get_channel_name(channel, channel_type)
        return self._client.authenticate(channel, socket)