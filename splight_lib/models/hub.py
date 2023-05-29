from typing import List, Optional, ClassVar

from pydantic import BaseModel, PrivateAttr, validator
from splight_lib.client.hub.abstract import AbstractHubClient
from splight_lib.client.hub.client import SplightHubClient
from splight_lib.settings import settings


VERIFICATION_CHOICES = ["verified", "unverified", "official"]


class classproperty(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class HubComponent(BaseModel):
    id: Optional[str]
    name: str
    splight_cli_version: str
    build_status: Optional[str]
    description: Optional[str]
    privacy_policy: Optional[str] = None
    component_type: Optional[str] = None
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

    @validator("verification", pre=True, always=True)
    def set_verification_now(cls, v):
        if v:
            assert v in VERIFICATION_CHOICES, "Verification value not allowed."
        return v

    @classproperty
    def mine(cls) -> AbstractHubClient:
        return SplightHubClient(
            scope='mine',
            resource_type=cls,
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )

    @classproperty
    def all(cls) -> AbstractHubClient:
        return SplightHubClient(
            scope='all',
            resource_type=cls,
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )

    @classproperty
    def public(cls) -> AbstractHubClient:
        return SplightHubClient(
            scope='public',
            resource_type=cls,
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )

    @classproperty
    def private(cls) -> AbstractHubClient:
        return SplightHubClient(
            scope='private',
            resource_type=cls,
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )

    @classproperty
    def setup(cls) -> AbstractHubClient:
        return SplightHubClient(
            scope='setup',
            resource_type=cls,
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )


class HubComponentVersion(HubComponent):
    pass
