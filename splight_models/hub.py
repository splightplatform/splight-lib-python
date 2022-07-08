from typing import List, Any, Optional
from pydantic import validator
from .base import SplightBaseModel
from enum import Enum

IMPACT_CHOICES = [i for i in range(1,6)]
VERIFICATION_CHOICES = ['verified', 'unverified', 'official']

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

    @validator('impact', pre=True, always=True)
    def set_impact_now(cls, v):
        if v:
            assert v in IMPACT_CHOICES, 'Impact value not allowed.'
        return v

    @validator('verification', pre=True, always=True)
    def set_verification_now(cls, v):
        if v:
            assert v in VERIFICATION_CHOICES, 'Verification value not allowed.'
        return v


class HubAlgorithm(HubComponent):
    pass


class HubNetwork(HubComponent):
    pass


class HubConnector(HubComponent):
    pass
