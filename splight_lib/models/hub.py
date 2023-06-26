import json
import os
from glob import glob
from typing import List, Optional

import py7zr
from pydantic import BaseModel, PrivateAttr, validator
from splight_lib.client.hub.abstract import AbstractHubClient
from splight_lib.client.hub.client import SplightHubClient
from splight_lib.models.component import (
    Binding,
    Command,
    ComponentType,
    Endpoint,
    InputParameter,
    Output,
)
from splight_lib.settings import settings
from splight_lib.utils.hub import (
    COMPRESSION_TYPE,
    README_FILE_1,
    README_FILE_2,
    get_ignore_pathspec,
    get_spec,
)

VERIFICATION_CHOICES = ["verified", "unverified", "official"]


def get_hub_client() -> AbstractHubClient:
    return SplightHubClient(
        access_key=settings.SPLIGHT_ACCESS_ID,
        secret_key=settings.SPLIGHT_SECRET_KEY,
        api_host=settings.SPLIGHT_PLATFORM_API_HOST,
    )


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

    input: List[InputParameter] = []
    output: List[Output] = []
    commands: List[Command] = []
    endpoints: List[Endpoint] = []
    bindings: List[Binding] = []

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
        data = hub_client.mine.get(resource_type=cls.__name__, **params)
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_all(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.all.get(resource_type=cls.__name__, **params)
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_public(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.public.get(resource_type=cls.__name__, **params)
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_private(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.private.get(resource_type=cls.__name__, **params)
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_setup(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.setup.get(resource_type=cls.__name__, **params)
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def retrieve_mine(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.mine.get(
            resource_type=cls.__name__, id=id, first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_all(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.all.get(
            resource_type=cls.__name__, id=id, first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_public(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.public.get(
            resource_type=cls.__name__, id=id, first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_private(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.private.get(
            resource_type=cls.__name__, id=id, first=True
        )
        return cls.parse_obj(data)

    @classmethod
    def retrieve_setup(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.setup.get(
            resource_type=cls.__name__, id=id, first=True
        )
        return cls.parse_obj(data)

    def delete(self):
        return self._hub_client.mine.delete(self.id)

    def download(self):
        return self._hub_client.download(data=self.dict())

    @classmethod
    def upload(cls, path: str):
        hub_client = get_hub_client()
        spec = get_spec(path)
        name = spec["name"]
        version = spec["version"]
        file_name = f"{name}-{version}.{COMPRESSION_TYPE}"
        ignore_pathspec = get_ignore_pathspec(path)
        versioned_name = f"{name}-{version}"
        readme_path = os.path.join(path, README_FILE_1)
        if not os.path.exists(readme_path):
            readme_path = os.path.join(path, README_FILE_2)
        with py7zr.SevenZipFile(file_name, "w") as archive:
            all_files = glob(f"{path}/**", recursive=True)
            for filename in all_files:
                if ignore_pathspec and ignore_pathspec.match_file(filename):
                    continue
                if os.path.isdir(filename):
                    continue
                filepath = filename.replace(path, f"{versioned_name}/")
                archive.write(filename, filepath)

        data = {
            "name": name,
            "version": version,
            "splight_cli_version": spec["splight_cli_version"],
            "privacy_policy": spec.get("privacy_policy", "private"),
            "tags": spec.get("tags", []),
            "custom_types": json.dumps(spec.get("custom_types", [])),
            "input": json.dumps(spec.get("input", [])),
            "output": json.dumps(spec.get("output", [])),
            "component_type": spec.get(
                "component_type", ComponentType.CONNECTOR.value
            ),
            "commands": json.dumps(spec.get("commands", [])),
            "bindings": json.dumps(spec.get("bindings", [])),
            "endpoints": json.dumps(spec.get("endpoints", [])),
        }
        files = {
            "file": open(file_name, "rb"),
            "readme": open(readme_path, "rb"),
        }
        component = hub_client.upload(data=data, files=files)
        if os.path.exists(file_name):
            os.remove(file_name)
        return cls.parse_obj(component)


class HubComponentVersion(HubComponent):
    pass
