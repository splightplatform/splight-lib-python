from abc import ABCMeta, abstractmethod

class Data:
    pass


class AbstractComunication(metaclass=ABCMeta):

    @abstractmethod
    def send(self):
        pass
    
    @abstractmethod
    def receive(self):
        pass


class ZeroQueueCommunication(AbstractComunication):
    def __init__(self, *args, **kwargs):
        self.client = None

    def send(self, data: Data):
        self.client.send(data)

    def receive(self) -> Data:
        return self.client.receive()

