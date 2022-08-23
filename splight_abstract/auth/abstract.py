from abc import ABC, abstractmethod


class AbstractAuthClient(ABC):
    @property
    @abstractmethod
    def credentials(self):
        pass

    @property
    @abstractmethod
    def profile(self):
        pass

    @property
    @abstractmethod
    def role(self):
        pass

    @property
    @abstractmethod
    def user(self):
        pass

    @property
    @abstractmethod
    def organization(self):
        pass

    @property
    @abstractmethod
    def organizations(self):
        pass

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def authenticate_header(self):
        pass
