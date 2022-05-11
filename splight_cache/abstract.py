from client import AbstractClient
from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List, Callable


class AbstractCacheClient(AbstractClient):

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def delete(self, key):
        pass

    @abstractmethod
    def clear(self):
        pass
