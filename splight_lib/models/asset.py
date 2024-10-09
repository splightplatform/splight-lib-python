import warnings
from typing import Any

from geojson_pydantic import GeometryCollection

from splight_lib.models.attribute import Attribute
from splight_lib.models.database_base import (
    ResourceSummary,
    SplightDatabaseBaseModel,
)
from splight_lib.models.exceptions import MethodNotAllowed
from splight_lib.models.metadata import Metadata
from splight_lib.models.tag import Tag

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


class Asset(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    tags: list[Tag] = []
    attributes: list[Attribute] = []
    metadata: list[Metadata] = []
    geometry: GeometryCollection | None = None
    centroid_coordinates: tuple[float, float] | None = None
    kind: AssetKind | None = None
    actions: list[ResourceSummary] | None = None
    related_to: list[AssetRelationship] = []
    related_from: list[AssetRelationship] = []

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
