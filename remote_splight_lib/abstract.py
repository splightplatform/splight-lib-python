from abc import ABC, abstractmethod


class SplightAPIClientAbstract(ABC):
    @property
    @abstractmethod
    def algorithm(self):
        pass

    @property
    @abstractmethod
    def asset(self):
        pass

    @property
    @abstractmethod
    def attribute(self):
        pass

    @property
    @abstractmethod
    def blockchain(self):
        pass

    @property
    @abstractmethod
    def connector(self):
        pass

    @property
    @abstractmethod
    def datalake(self):
        pass

    @property
    @abstractmethod
    def deployment(self):
        pass

    @property
    @abstractmethod
    def hub(self):
        pass

    @property
    @abstractmethod
    def mapping(self):
        pass

    @property
    @abstractmethod
    def network(self):
        pass

    @property
    @abstractmethod
    def rule(self):
        pass

    @property
    @abstractmethod
    def storage(self):
        pass

    @property
    @abstractmethod
    def common_storage(self):
        pass

    @property
    @abstractmethod
    def tag(self):
        pass
