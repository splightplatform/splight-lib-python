import json
from enum import Enum
from pydantic import BaseModel
from typing import Dict, Optional, Callable
from abc import abstractmethod, abstractproperty
from splight_abstract.client import AbstractClient
from splight_models import NotificationContext
from splight_models.notification import NotificationUserData


class CommunicationClientStatus(str, Enum):
    STARTING = 'starting'
    READY = 'ready'
    FAILED = 'failed'
    ERROR =  'error'


class CommunicationContext(NotificationContext):
    auth_headers: Optional[Dict] = None
    user_data: Optional[NotificationUserData] = None


class AbstractCommunicationClient(AbstractClient):
    @abstractproperty
    def status(self):
        pass

    @staticmethod
    def default_handler(func: Callable, model: BaseModel, data: str):
        data = json.loads(data)
        return func(**(model(**data).dict()))

    @abstractmethod
    def add_handler(self, event_name: str, event_handler: Callable) -> None:
        pass

    @abstractmethod
    def remove_handler(self, event_name: str, event_handler: Callable) -> None:
        pass
