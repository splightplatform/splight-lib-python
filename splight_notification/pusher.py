from pusher import Pusher
from splight_models.notification import Notification
from .abstract import AbstractNotificationClient
from .settings import PUSHER_CONFIG


class PusherClient(AbstractNotificationClient):
    def __init__(self, *args, **kwargs):
        super(PusherClient, self).__init__(*args, **kwargs)
        self._client = Pusher(**PUSHER_CONFIG)
        
    @property
    def channel(self):
        return f"private-{self.namespace}"

    def send(self, instance: Notification, topic: str = 'default') -> None:
        self._client.trigger(self.channel, topic, instance.dict())
