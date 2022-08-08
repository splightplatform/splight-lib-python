from .base import SplightBaseModel
from typing import Optional, List
from splight_models.runner import Parameter
from enum import Enum


class ComponentSize(str, Enum):
    small_component_size = 'small'
    medium_component_size = 'medium'
    large_component_size = 'large'
    very_large_component_size = 'very_large'


class Deployment(SplightBaseModel):
    id: Optional[str] = None
    type: str  # eg. Connector, Network, Algorithm
    external_id: str = None  # eg. 1
    version: str  # eg. Forecasting-0_2
    parameters: List[Parameter] = []
    namespace: Optional[str] = None
    component_capacity: Optional[str] = ComponentSize.medium_component_size
