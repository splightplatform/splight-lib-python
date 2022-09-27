from abc import abstractmethod, abstractproperty
from splight_models import Notification, NotificationContext
from splight_abstract.client import AbstractClient


class AbstractNotificationClient(AbstractClient):
    @abstractmethod
    def send(self, instance: Notification, topic: str = 'default') -> None:
        self._client.trigger(self.channel, topic, instance.dict())

    @abstractproperty
    def context(self) -> NotificationContext:
        pass
