from typing import List, Any, Optional
from .base import SplightBaseModel


class Parameter(SplightBaseModel):
    name: str
    type: str = "str"
    required: bool = False
    multiple: bool = False
    value: Any = None


class HubComponent(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    version: str
    privacy_policy: str
    tenant: str
    parameters: List[Parameter] = []
    impact: Optional[int]
    readme_url: str
    picture_url: str
    verification: str
    last_modified: str


class HubAlgorithm(HubComponent):
    pass


class HubNetwork(HubComponent):
    pass


class HubConnector(HubComponent):
    pass
