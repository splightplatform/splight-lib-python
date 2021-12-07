from .abstract import AbstractComponent


class AbstractNetworkComponent(AbstractComponent):

    @property
    def name(self):
        return self.__class__.__name__
