from abc import abstractmethod
from client import AbstractClient
from splight_models import Notification


class AbstractNotificationClient(AbstractClient):

    @abstractmethod
    def send(self, instance: Notification, topic: str = 'default') -> None:
        self._client.trigger(self.channel, topic, instance.dict())
