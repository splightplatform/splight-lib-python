
from .abstract import AbstractComponent
from splight_models import Algorithm


class AbstractAlgorithmComponent(AbstractComponent):
    managed_class = Algorithm
