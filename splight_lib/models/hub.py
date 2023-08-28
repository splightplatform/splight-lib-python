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
    CustomType,
    Endpoint,
    InputParameter,
    Output,
    Routine,
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

    custom_types: List[CustomType] = []
    input: List[InputParameter] = []
    output: List[Output] = []
    routines: List[Routine] = []
    custom_types: List[CustomType] = []
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
        params["organization_id"] = hub_client.get_org_id()
        data = hub_client.get(**params)
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_all(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.get(**params)
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_public(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        params["privacy_policy"] = "public"
        data = hub_client.get(**params)
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def list_private(cls, **params) -> List["HubComponent"]:
        params["privacy_policy"] = "private"
        hub_client = get_hub_client()
        data = hub_client.get(**params)
        return [cls.parse_obj(obj) for obj in data]

    @classmethod
    def retrieve(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.get(id=id, first=True)
        return cls.parse_obj(data)

    def delete(self):
        hub_client = get_hub_client()
        return hub_client.delete(self.id)

    def download(self):
        hub_client = get_hub_client()
        params = {"name": self.name, "version": self.version}
        return hub_client.download(data=params)

    @classmethod
    def upload(cls, path: str):
        hub_client = get_hub_client()
        spec = get_spec(path)
        name = spec["name"]
        version = spec["version"]
        file_name = f"{name}-{version}.{COMPRESSION_TYPE}"
        ignore_pathspec = get_ignore_pathspec(path)
        versioned_path = f"{name}-{version}"
        readme_path = os.path.join(path, README_FILE_1)
        if not os.path.exists(readme_path):
            readme_path = os.path.join(path, README_FILE_2)
        with py7zr.SevenZipFile(file_name, "w") as archive:
            all_files = glob(f"{path}/**", recursive=True)
            for filepath in all_files:
                if ignore_pathspec and ignore_pathspec.match_file(filepath):
                    continue
                if os.path.isdir(filepath):
                    continue
                rel_filename = os.path.relpath(filepath, path)
                new_filepath = os.path.join(versioned_path, rel_filename)
                archive.write(filepath, new_filepath)

        spec["name"] = name
        spec["version"] = version
        spec.setdefault("component_type", ComponentType.CONNECTOR.value)
        data_cls = cls.parse_obj(spec)

        data = data_cls.dict(exclude_none=True)

        to_json = [
            "tags",
            "routines",
            "custom_types",
            "input",
            "output",
            "commands",
            "bindings",
            "endpoints",
        ]
        for key in to_json:
            data[key] = json.dumps(data[key])

        files = {
            "file": open(file_name, "rb"),
            "readme": open(readme_path, "rb"),
        }
        try:
            component = hub_client.upload(data=data, files=files)
        except Exception as exc:
            raise Exception("unable to push component") from exc
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
        return cls.parse_obj(component)
