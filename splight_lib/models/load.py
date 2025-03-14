from typing import Any

from pydantic import model_validator

from splight_lib.models import AssetParams, AssetRelationship, Attribute
from splight_lib.models.database_base import SplightDatabaseBaseModel
from splight_lib.settings import SplightAPIVersion, api_settings


class Load(AssetParams, SplightDatabaseBaseModel):
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None
    switch_status: Attribute | None = None
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None

    @model_validator(mode="after")
    @classmethod
    def check_api_version(cls, data: Any) -> Any:
        if api_settings.API_VERSION == SplightAPIVersion.V3:
            raise NotImplementedError("Load kind is not supported in API v3.")
        return data
