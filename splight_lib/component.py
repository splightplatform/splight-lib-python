from abc import ABCMeta, abstractmethod
from splight_storage.models.component import (
    DigitalOffer,
    RunningDigitalOffer,
    DigitalOfferComponent,
)


class DigitalOfferComponentInterface(metaclass=ABCMeta):

    @abstractmethod
    def execute(self):
        pass
