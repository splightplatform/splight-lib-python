from abc import ABC, abstractmethod


class AbstractAuthClient(ABC):
    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def authenticate_header(self):
        pass
