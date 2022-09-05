from typing import List, Any, Optional
from pydantic import validator
from .base import SplightBaseModel
from enum import Enum

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
    version: str
    privacy_policy: Optional[str] = None
    tenant: Optional[str] = None
    parameters: List[Parameter] = []
    readme_url: Optional[str]
    picture_url: Optional[str]
    verification: Optional[str]
    created_at: Optional[str]
    last_modified: Optional[str]
    tags: List[str] = []

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

