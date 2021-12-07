from abc import ABCMeta, abstractmethod


class AbstractCommunication(metaclass=ABCMeta):

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def receive(self):
        pass
