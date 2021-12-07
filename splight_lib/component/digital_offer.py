from .abstract import AbstractComponent


class AbstractDigitalOfferComponent(AbstractComponent):

    @property
    def name(self):
        return self.__class__.__name__
