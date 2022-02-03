from typing import Dict
from abc import ABCMeta, abstractmethod


class AbstractNotificationClient(metaclass=ABCMeta):

    @abstractmethod
    def authenticate(self, socket: str) -> None:
        pass

    @abstractmethod
    def send(self, topic: str, data: Dict) -> None:
        pass
