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
    privacy_policy: Optional[str] = None
    tenant: Optional[str] = None
    parameters: List[Parameter] = []
    readme_url: Optional[str]
    picture_url: Optional[str]
    verification: Optional[str]
    impact: Optional[int]
    last_modified: Optional[str]


class HubAlgorithm(HubComponent):
    pass


class HubNetwork(HubComponent):
    pass


class HubConnector(HubComponent):
    pass
