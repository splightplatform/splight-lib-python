import logging
from .base import SplightBaseModel
from typing import Optional, List
from splight_models.runner import Parameter
from enum import Enum


class ComponentSize(str, Enum):
    small = 'small'
    medium = 'medium'
    large = 'large'
    very_large = 'very_large'


class RestartPolicy(str, Enum):
    never = 'Never'
    on_failure = 'OnFailure'
    always = 'Always'


class LogginLevel(str, Enum):
    critical = logging.CRITICAL
    error = logging.ERROR
    warning = logging.WARNING
    info = logging.INFO
    debug = logging.DEBUG
    notset = logging.NOTSET


class Deployment(SplightBaseModel):
    id: Optional[str] = None
    type: str  # eg. Connector, Network, Algorithm
    external_id: str = None  # eg. 1
    version: str  # eg. Forecasting-0_2
    parameters: List[Parameter] = []
    namespace: Optional[str] = None
    component_capacity: str = ComponentSize.medium.value
    log_level: int = LogginLevel.debug.value
    restart_policy: str = RestartPolicy.always.value
