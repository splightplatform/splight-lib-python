from typing import Optional
from pydantic import validator
from splight_models.component import BaseComponent
from typing import List

VERIFICATION_CHOICES = ['verified', 'unverified', 'official']


class HubComponent(BaseComponent):
    id: Optional[str]
    name: str
    splight_cli_version: str
    build_status: Optional[str]
    description: Optional[str]
    privacy_policy: Optional[str] = None
    tenant: Optional[str] = None
    readme: Optional[str]
    picture: Optional[str]
    file: Optional[str]
    verification: Optional[str]
    created_at: Optional[str]
    last_modified: Optional[str]
    tags: List[str] = []
    min_component_capacity: Optional[str]
    usage_count: int = 0

    @validator('verification', pre=True, always=True)
    def set_verification_now(cls, v):
        if v:
            assert v in VERIFICATION_CHOICES, 'Verification value not allowed.'
        return v


class HubComponentVersion(HubComponent):
    pass
