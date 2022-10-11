from enum import Enum
from typing import Callable, Dict
from abc import abstractmethod, abstractproperty
from splight_abstract.client import AbstractClient
from splight_models import CommunicationContext, CommunicationEvent


class CommunicationClientStatus(str, Enum):
    STARTING = 'starting'
    READY = 'ready'
    FAILED = 'failed'
    ERROR =  'error'


class AbstractCommunicationClient(AbstractClient):
    def __init__(self, instance_id: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance_id = instance_id

    @abstractproperty
    def context(self) -> CommunicationContext:
        pass
    
    @abstractproperty
    def status(self):
        pass

    @abstractmethod
    def bind(self, event_name: str, event_handler: Callable) -> None:
        pass

    @abstractmethod
    def unbind(self, event_name: str, event_handler: Callable) -> None:
        pass

    @abstractmethod
    def trigger(self, event: CommunicationEvent):
        pass

    @abstractmethod
    def authenticate(self, channel_name: str, socket_id: str, custom_data: Dict = None) -> dict:
        pass
