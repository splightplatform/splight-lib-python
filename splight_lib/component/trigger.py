from .abstract import AbstractComponent


class AbstractTriggerGroupComponent(AbstractComponent):

    @property
    def name(self):
        return self.__class__.__name__
