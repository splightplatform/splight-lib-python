from typing import List, Optional, ClassVar

from pydantic import BaseModel, PrivateAttr, validator
from splight_lib.client.hub.abstract import AbstractHubClient
from splight_lib.client.hub.client import SplightHubClient
from splight_lib.settings import settings
from splight_lib.utils.hub import get_ignore_pathspec, COMPRESSION_TYPE
import os
import py7zr


VERIFICATION_CHOICES = ["verified", "unverified", "official"]


def get_hub_client() -> AbstractHubClient:
    return SplightHubClient(
        access_key=settings.SPLIGHT_ACCESS_ID,
        secret_key=settings.SPLIGHT_SECRET_KEY,
        api_host=settings.SPLIGHT_PLATFORM_API_HOST,
    )


class classproperty(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class HubComponent(BaseModel):
    id: Optional[str]
    name: str
    version: str
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
        self._hub_client = get_hub_client()

    @validator("verification", pre=True, always=True)
    def set_verification_now(cls, v):
        if v:
            assert v in VERIFICATION_CHOICES, "Verification value not allowed."
        return v

    @classmethod
    def list_mine(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.mine.get(
            resource_type=cls.__name__,
            **params
        )
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_all(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.all.get(
            resource_type=cls.__name__,
            **params
        )
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_public(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.public.get(
            resource_type=cls.__name__,
            **params
        )
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_private(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.private.get(
            resource_type=cls.__name__,
            **params
        )
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_setup(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.setup.get(
            resource_type=cls.__name__,
            **params
        )
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def retrieve_mine(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.mine.get(
            resource_type=cls.__name__,
            id=id,
            first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_all(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.all.get(
            resource_type=cls.__name__,
            id=id,
            first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_public(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.public.get(
            resource_type=cls.__name__,
            id=id,
            first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_private(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.private.get(
            resource_type=cls.__name__,
            id=id,
            first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_setup(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.setup.get(
            resource_type=cls.__name__,
            id=id,
            first=True
        )
        return cls.parse_obj(data)

    def delete(self):
        return self._hub_client.mine.delete(self.id)

    def download(self):
        data, _ = self._hub_client.download(data=self.dict())
        return data

    def upload(self, path: str):
        file_name = f"{self.name}-{self.version}.{COMPRESSION_TYPE}"
        ignore_pathspec = get_ignore_pathspec(path)
        versioned_name = f"{self.name}-{self.version}"
        with py7zr.SevenZipFile(file_name, "w") as archive:
            for root, _, files in os.walk(path):
                if ignore_pathspec and ignore_pathspec.match_file(root):
                    continue
                for file in files:
                    if ignore_pathspec and ignore_pathspec.match_file(
                        os.path.join(root, file)
                    ):
                        continue
                    filepath = os.path.join(root, file)
                    archive.write(
                        filepath, os.path.join(versioned_name, file)
                    )


class HubComponentVersion(HubComponent):
    pass
