from typing import Optional
from pydantic import validator
from .runner import BaseRunner
from typing import List

VERIFICATION_CHOICES = ['verified', 'unverified', 'official']


class HubComponent(BaseRunner):
    id: Optional[str]
    name: str
    type: str = None
    description: Optional[str]
    privacy_policy: Optional[str] = None
    tenant: Optional[str] = None
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


class HubComponentVersion(HubComponent):
    pass
