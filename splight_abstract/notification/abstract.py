from abc import abstractmethod
from typing import Dict
from splight_models import Notification
from splight_abstract.client import AbstractClient


class AbstractNotificationClient(AbstractClient):

    @abstractmethod
    def send(self, instance: Notification, topic: str = 'default') -> None:
        pass
        # self._client.trigger(self.channel, topic, instance.dict())

    @abstractmethod
    def authenticate(self, channel_name: str, socket_id: str) -> Dict:
        pass
