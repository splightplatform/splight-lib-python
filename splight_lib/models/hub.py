import json
import os
import warnings
from enum import auto
from glob import glob
from typing import Any, List, Optional

import py7zr
from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    ValidationInfo,
    model_validator,
)
from strenum import LowercaseStrEnum

from splight_lib.client.hub.abstract import AbstractHubClient
from splight_lib.client.hub.client import SplightHubClient
from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.component import (
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

warnings.simplefilter("always", DeprecationWarning)


class HubComponentVerificationEnum(LowercaseStrEnum):
    VERIFIED = auto()
    UNVERIFIED = auto()
    OFFICIAL = auto()


def get_hub_client() -> AbstractHubClient:
    return SplightHubClient(
        access_key=settings.SPLIGHT_ACCESS_ID,
        secret_key=settings.SPLIGHT_SECRET_KEY,
        api_host=settings.SPLIGHT_PLATFORM_API_HOST,
    )


# TODO: Unify HubComponent model to be a SplightDatabaseBaseModel an use
# SplightDatabaseClient. The same as HubSolution
class HubComponent(BaseModel):
    id: Optional[str] = None
    name: str
    version: str
    splight_lib_version: Optional[str] = None
    splight_cli_version: Optional[str] = None
    build_status: Optional[str] = None
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    privacy_policy: Optional[str] = None
    component_type: ComponentType = ComponentType.CONNECTOR
    readme: Optional[str] = None
    file: Optional[str] = None
    verification: Optional[HubComponentVerificationEnum] = None
    tags: List[str] = []

    custom_types: List[CustomType] = []
    input: List[InputParameter] = []
    output: List[Output] = []
    routines: List[Routine] = []
    custom_types: List[CustomType] = []
    endpoints: List[Endpoint] = []

    _hub_client: AbstractHubClient = PrivateAttr()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hub_client = get_hub_client()

    @model_validator(mode="before")
    def check_lib_version(cls, data: Any, info: ValidationInfo) -> Any:
        if cli_version := data.get("splight_cli_version"):
            warnings.warn(
                (
                    "splight_cli_version is deprecated"
                    "use splight_lib_version instead"
                ),
                DeprecationWarning,
                stacklevel=2,
            )

        if not data.get("splight_lib_version") and not cli_version:
            raise ValueError("splight_lib_version is required")
        return data

    @classmethod
    def list_mine(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        params["organization_id"] = hub_client.get_org_id()
        data = hub_client.get(**params).data
        return [cls.model_validate(obj) for obj in data]

    @classmethod
    def list_all(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        data = hub_client.get(**params).data
        return [cls.model_validate(obj) for obj in data]

    @classmethod
    def list_public(cls, **params) -> List["HubComponent"]:
        hub_client = get_hub_client()
        params["privacy_policy"] = "public"
        data = hub_client.get(**params).data
        return [cls.model_validate(obj) for obj in data]

    @classmethod
    def list_private(cls, **params) -> List["HubComponent"]:
        params["privacy_policy"] = "private"
        hub_client = get_hub_client()
        data = hub_client.get(**params).data
        return [cls.model_validate(obj) for obj in data]

    @classmethod
    def retrieve(cls, id: str) -> "HubComponent":
        hub_client = get_hub_client()
        data = hub_client.get(id=id, first=True)
        return cls.model_validate(data)

    def delete(self):
        hub_client = get_hub_client()
        return hub_client.delete(self.id)

    def download(self):
        hub_client = get_hub_client()
        return hub_client.download(id=self.id, name=self.name, type="source")

    def save(self):
        hub_client = get_hub_client()
        saved = hub_client.save(instance=self.model_dump())
        if not self.id:
            self.id = saved["id"]

    def build(self):
        hub_client = get_hub_client()
        return hub_client.build(id=self.id)

    @classmethod
    def upload(cls, path: str, image_file: str):
        hub_client = get_hub_client()
        image_path = os.path.join(path, image_file)
        spec = get_spec(path)
        name = spec["name"]
        version = spec["version"]
        raw_hub_component = hub_client.get(
            name=name, version=version, first=True
        )

        hub_component = HubComponent.model_validate(spec)
        if raw_hub_component:
            old_hub_component = HubComponent.model_validate(raw_hub_component)
            hub_component.id = old_hub_component.id
        hub_component.save()

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
                if image_file in filepath:
                    continue
                rel_filename = os.path.relpath(filepath, path)
                new_filepath = os.path.join(versioned_path, rel_filename)
                archive.write(filepath, new_filepath)

        spec["name"] = name
        spec["version"] = version
        spec.setdefault("component_type", ComponentType.CONNECTOR.value)
        data_cls = cls.model_validate(spec)

        # TODO: Check if this is needed
        data = data_cls.model_dump(exclude_none=True)

        to_json = [
            "tags",
            "routines",
            "custom_types",
            "input",
            "output",
            "endpoints",
        ]
        for key in to_json:
            data[key] = json.dumps(data[key])

        try:
            hub_client.upload(
                id=hub_component.id, file_path=file_name, type_="source"
            )
            hub_client.upload(
                id=hub_component.id, file_path=readme_path, type_="readme"
            )
            hub_client.upload(
                id=hub_component.id, file_path=image_path, type_="image"
            )
        except Exception as exc:
            raise exc
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
            if os.path.exists(image_path):
                os.remove(image_path)

        return hub_component
