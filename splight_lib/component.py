from abc import ABCMeta, abstractmethod
from splight_storage.models.component import (
    DigitalOffer,
    RunningDigitalOffer,
    DigitalOfferComponent,
)
from threading import Thread

class ComponentInterface(metaclass=ABCMeta):
    @abstractmethod
    def init(self) -> None:
        pass

    @abstractmethod
    def run(self)-> None:
        pass

    @abstractmethod
    def refresh_mapping(self) -> None: 
        pass

    @abstractmethod
    def read_from_master(self) -> None:
        pass

    @abstractmethod
    def watchdog(self) -> None:
        pass

    def execute(self) -> None:
        # TODO: define a way to identify the object that use this component
        self.init()
        threads = [
            Thread(target=self.run),
            Thread(target=self.refresh_mapping),
            Thread(target=self.read_from_master),
            Thread(target=self.watchdog),
        ]
        for thread in threads:
            thread.start()


class DigitalOfferComponentInterface(ComponentInterface):

    @property
    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def execute(self):
        pass
