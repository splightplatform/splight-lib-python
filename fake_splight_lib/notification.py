from splight_notification.abstract import AbstractNotificationClient
from typing import Dict, Optional
from splight_models import Channel

class FakeNotificationClient(AbstractNotificationClient):

    def get_channel_name(self, channel: str, channel_type: Channel):
        return f"{channel_type.value}-{self.namespace}-{channel}"

    def send(self, topic: str, data: Dict, channel: str = "default", channel_type: Channel = Channel.PRIVATE):
        self.logger.debug(f"{__class__.__name__} Sent data: {data} {topic}")

    def authenticate(self, socket: str, channel: str = "default", channel_type: Channel = Channel.PRIVATE) -> Dict:
        return {"auth": "abc123"}