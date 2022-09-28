import json
from enum import Enum
from pydantic import BaseModel
from typing import Callable
from abc import abstractmethod, abstractproperty
from splight_abstract.client import AbstractClient
from splight_models import CommunicationContext


class CommunicationClientStatus(str, Enum):
    STARTING = 'starting'
    READY = 'ready'
    FAILED = 'failed'
    ERROR =  'error'


class AbstractCommunicationClient(AbstractClient):
    @abstractproperty
    def context(self) -> CommunicationContext:
        pass
    
    @abstractproperty
    def status(self):
        pass

    @staticmethod
    def default_handler(func: Callable, model: BaseModel, data: str):
        data = json.loads(data)
        return func(**(model(**data).dict()))

    @abstractmethod
    def bind(self, event_name: str, event_handler: Callable) -> None:
        pass

    @abstractmethod
    def unbind(self, event_name: str, event_handler: Callable) -> None:
        pass

    @abstractmethod
    def trigger(self, event_name: str, event_handler: Callable) -> None:
        pass

    @abstractmethod
    def authenticate(self, event_name: str, event_handler: Callable) -> None:
        pass
