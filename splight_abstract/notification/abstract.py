from abc import abstractmethod
from splight_models import Notification
from splight_abstract.client import AbstractClient


class AbstractNotificationClient(AbstractClient):
    @abstractmethod
    def send(self, instance: Notification, topic: str = 'default') -> None:
        self._client.trigger(self.channel, topic, instance.dict())
