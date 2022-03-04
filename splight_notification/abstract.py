from typing import Dict
from abc import ABCMeta, abstractmethod
from splight_lib.database import Channel


class AbstractNotificationClient(metaclass=ABCMeta):

    def __init__(self, namespace = "default"):
        self.namespace = namespace.replace("_","").lower()

    @abstractmethod
    def get_channel_name(self, channel: str, channel_type: Channel) -> str:
        pass

    @abstractmethod
    def send(self, topic: str, data: Dict, channel: str = "default", channel_type: Channel = Channel.PRIVATE) -> None:
        pass

    @abstractmethod
    def authenticate(self, socket: str, channel: str = "default", channel_type: Channel = Channel.PRIVATE) -> Dict:
        pass

