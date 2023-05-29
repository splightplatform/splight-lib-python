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

    _hub_client: AbstractHubClient = PrivateAttr()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )

    @validator("verification", pre=True, always=True)
    def set_verification_now(cls, v):
        if v:
            assert v in VERIFICATION_CHOICES, "Verification value not allowed."
        return v

    @classmethod
    def list_mine(cls, **params):
        hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )
        data = hub_client.mine.get(
            resource_type=cls.__name__,
            **params
        )
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_all(cls, **params):
        hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )
        data = hub_client.all.get(
            resource_type=cls.__name__,
            **params
        )
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_public(cls, **params):
        hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )
        data = hub_client.public.get(
            resource_type=cls.__name__,
            **params
        )
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_private(cls, **params):
        hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )
        data = hub_client.private.get(
            resource_type=cls.__name__,
            **params
        )
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_setup(cls, **params):
        hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )
        data = hub_client.setup.get(
            resource_type=cls.__name__,
            **params
        )
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def retrieve_mine(cls, id: str):
        hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )
        data = hub_client.mine.get(
            resource_type=cls.__name__,
            id=id,
            first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_all(cls, id: str):
        hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )
        data = hub_client.all.get(
            resource_type=cls.__name__,
            id=id,
            first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_public(cls, id: str):
        hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )
        data = hub_client.public.get(
            resource_type=cls.__name__,
            id=id,
            first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_private(cls, id: str):
        hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )
        data = hub_client.private.get(
            resource_type=cls.__name__,
            id=id,
            first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_setup(cls, id: str):
        hub_client = SplightHubClient(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            api_host=settings.SPLIGHT_PLATFORM_API_HOST,
        )
        data = hub_client.setup.get(
            resource_type=cls.__name__,
            id=id,
            first=True
        )
        return cls.parse_obj(data)

    def delete(self):
        return self._hub_client.mine.delete(self.id)

    def download(self):
        pass

    def upload(self):
        pass


class HubComponentVersion(HubComponent):
    pass
