from abc import ABCMeta, abstractmethod
from splight_storage.models import (
    DigitalOffer,
    RunningDigitalOffer,
    DigitalOfferComponent,
)


class DigitalOfferComponentInterface(metaclass=ABCMeta):

    @abstractmethod
    def execute(self):
        pass

    def deploy(self):
        DigitalOfferComponent.objects.get_or_create(**self.__dict__)
