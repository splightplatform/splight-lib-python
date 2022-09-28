import json
from enum import Enum
from pydantic import BaseModel
from typing import Callable, Dict
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

    def default_handler(self, func: Callable, model: BaseModel, data: str):
        data = json.loads(data)
        try:
            return_value = func(**(model(**data).dict()))
            self.trigger(event_name=func.__name__ + "_response", data={"response": return_value, "exception": None})
        except Exception as e:
            self.trigger(event_name=func.__name__ + "_response", data={"response": None, "exception": str(e)})
            raise e
        return return_value

    @abstractmethod
    def bind(self, event_name: str, event_handler: Callable) -> None:
        pass

    @abstractmethod
    def unbind(self, event_name: str, event_handler: Callable) -> None:
        pass

    @abstractmethod
    def trigger(self, event_name: str, data: Dict, socket_id: str = None, reference_id: str = None):
        pass

    @abstractmethod
    def authenticate(self, channel_name: str, socket_id: str, custom_data: Dict = None) -> dict:
        pass
