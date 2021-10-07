from enum import Enum
from abc import ABCMeta, abstractmethod


class ConnectorTypes(Enum):
    FILESYSTEM = 1
    QUEUE = 2
    DATABASE = 3
    SPLIGHT = 4
    FAKE = 5


class ConnectorInterface(metaclass=ABCMeta):
    type = None
    
    @abstractmethod
    def read(self):
        pass
