from .base import SplightBaseModel
from typing import Optional, List
from splight_models.runner import Parameter


class Deployment(SplightBaseModel):
    id: Optional[str] = None
    type: str  # eg. Connector, Network, Algorithm
    external_id: str = None  # eg. 1
    version: str  # eg. Forecasting-0_2
    parameters: List[Parameter] = []
    namespace: Optional[str] = None
