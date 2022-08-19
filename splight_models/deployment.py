import logging
from splight_models.base import SplightBaseModel
from typing import Optional, List
from splight_models.runner import Parameter
from enum import Enum


class ComponentSize(str, Enum):
    small = 'small'
    medium = 'medium'
    large = 'large'
    very_large = 'very_large'


class LogginLevel(str, Enum):
    critical = logging.CRITICAL
    error = logging.ERROR
    warning = logging.WARNING
    info = logging.INFO
    debug = logging.DEBUG
    notset = logging.NOTSET


class Deployment(SplightBaseModel):
    # run-spec
    id: Optional[str] = None
    type: str  # eg. Connector, Network, Algorithm
    external_id: str = None  # eg. 1
    version: str  # eg. Forecasting-0_2
    parameters: List[Parameter] = []
    # Template vars for deployment
    namespace: Optional[str] = None
    component_capacity: str = ComponentSize.medium.value
    log_level: int = LogginLevel.debug.value
    # CLI pre setup
    access_id: str = None
    secret_key: str = None
    hub_api_host: str = None
    api_host: str = None

    @property
    def service_name(self):
        id = str(self.id).lower()
        type_id = str(self.type).lower()
        return f"service-{type_id}-{id}"

    @property
    def deployment_name(self):
        id = str(self.id).lower()
        type_id = str(self.type).lower()
        return f"deployment-{type_id}-{id}"
