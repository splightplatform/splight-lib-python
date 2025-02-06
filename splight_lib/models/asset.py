import warnings
from typing import Any
from zoneinfo import available_timezones

from geojson_pydantic import GeometryCollection
from pydantic import BaseModel, field_validator

from splight_lib.models.attribute import Attribute
from splight_lib.models.database_base import (
    ResourceSummary,
    SplightDatabaseBaseModel,
)
from splight_lib.models.exceptions import MethodNotAllowed
from splight_lib.models.metadata import Metadata
from splight_lib.settings import SplightAPIVersion, api_settings

warnings.filterwarnings("ignore", category=UserWarning)


class AssetKind(SplightDatabaseBaseModel):
    id: str | None = None
    name: str

    def save(self):
        raise MethodNotAllowed("AssetKind objects are read-only")

    def delete(self):
        raise MethodNotAllowed("AssetKind objects are read-only")


class AssetRelationship(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    related_asset_kind: AssetKind | None = None
    asset: ResourceSummary | None = None
    related_asset: ResourceSummary | None = None

    def save(self) -> None:
        if (
            self.id is not None
            and api_settings.API_VERSION == SplightAPIVersion.V4
        ):
            raise NotImplementedError(
                "Asset Relationship save operation is not supported in API v4"
            )
        super().save()

    def set(self, asset_id: str) -> None:
        if api_settings.API_VERSION == SplightAPIVersion.V3:
            raise NotImplementedError(
                "Asset Relationsip set operation is not supported in API v3"
            )
        self._db_client.operate(
            "set-asset-relationship",
            instance={
                "relationship": self.id,
                "related_asset": asset_id,
            },
        )


class AssetParams(BaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    tags: list[ResourceSummary] | None = None
    geometry: GeometryCollection | None = None
    centroid_coordinates: tuple[float, float] | None = None
    kind: AssetKind | None = None
    timezone: str | None = "UTC"


class Asset(AssetParams, SplightDatabaseBaseModel):
    attributes: list[Attribute] | None = None
    metadata: list[Metadata] | None = None
    related_to: list[AssetRelationship] | None = None
    related_from: list[AssetRelationship] | None = None

    def set_attribute(self, attribute: Attribute, value: Any, value_type: str):
        new_value = self._db_client.operate(
            resource_name="set-asset-attribute",
            instance={
                "asset": self.id,
                "attribute": attribute.id,
                "value": value,
                "type": value_type,
            },
        )
        return new_value

    def get_attribute(self, attribute: Attribute, value_type: str):
        new_value = self._db_client.operate(
            resource_name="get-asset-attribute",
            instance={
                "asset": self.id,
                "attribute": attribute.id,
                "type": value_type,
            },
        )
        return new_value

    @field_validator("timezone")
    def validate_timezone(cls, v):
        if v and v not in available_timezones():
            raise ValueError("Invalid timezone")
        return v
