import warnings
from enum import auto
from typing import Any

from pydantic import BaseModel, PrivateAttr, ValidationInfo, model_validator
from strenum import LowercaseStrEnum
from typing_extensions import Self

from splight_lib.client.hub.abstract import AbstractHubClient
from splight_lib.client.hub.client import SplightHubClient
from splight_lib.models._v3.component import (
    ComponentType,
    CustomType,
    Endpoint,
    InputParameter,
    Output,
    Routine,
)
from splight_lib.models._v3.exceptions import CommandDisable
from splight_lib.settings import workspace_settings

warnings.simplefilter("always", DeprecationWarning)


class HubComponentVerificationEnum(LowercaseStrEnum):
    VERIFIED = auto()
    UNVERIFIED = auto()
    OFFICIAL = auto()


def get_hub_client() -> AbstractHubClient:
    return SplightHubClient(
        access_key=workspace_settings.SPLIGHT_ACCESS_ID,
        secret_key=workspace_settings.SPLIGHT_SECRET_KEY,
        api_host=workspace_settings.SPLIGHT_PLATFORM_API_HOST,
    )


# TODO: Unify HubComponent model to be a SplightDatabaseBaseModel
class HubComponent(BaseModel):
    id: str | None = None
    name: str
    version: str
    splight_lib_version: str | None = None
    splight_cli_version: str | None = None
    build_status: str | None = None
    description: str | None = None
    privacy_policy: str | None = None
    component_type: ComponentType = ComponentType.CONNECTOR
    readme: str | None = None
    file: str | None = None
    verification: HubComponentVerificationEnum | None = None
    tags: list[str] = []

    custom_types: list[CustomType] = []
    input: list[InputParameter] = []
    output: list[Output] = []
    routines: list[Routine] = []
    custom_types: list[CustomType] = []
    endpoints: list[Endpoint] = []

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
    def list_mine(cls, **params) -> list[Self]:
        hub_client = get_hub_client()
        params["organization_id"] = hub_client.get_org_id()
        data = hub_client.get(**params).data
        return [cls.model_validate(obj) for obj in data]

    @classmethod
    def list_all(cls, **params) -> list[Self]:
        hub_client = get_hub_client()
        data = hub_client.get(**params).data
        return [cls.model_validate(obj) for obj in data]

    @classmethod
    def list_public(cls, **params) -> list[Self]:
        hub_client = get_hub_client()
        params["privacy_policy"] = "public"
        data = hub_client.get(**params).data
        return [cls.model_validate(obj) for obj in data]

    @classmethod
    def list_private(cls, **params) -> list[Self]:
        params["privacy_policy"] = "private"
        hub_client = get_hub_client()
        data = hub_client.get(**params).data
        return [cls.model_validate(obj) for obj in data]

    @classmethod
    def retrieve(cls, id: str) -> Self:
        hub_client = get_hub_client()
        data = hub_client.get(id=id, first=True)
        return cls.model_validate(data)

    def delete(self) -> None:
        hub_client = get_hub_client()
        return hub_client.delete(self.id)

    def save(self) -> None:
        raise CommandDisable("save method is not allowed")
