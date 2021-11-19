from abc import ABCMeta, abstractmethod
from splight_storage.models.component import (
    DigitalOffer,
    RunningDigitalOffer,
    DigitalOfferComponent,
)


class DigitalOfferComponentInterface(metaclass=ABCMeta):

    @property
    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def execute(self):
        pass
