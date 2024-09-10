import warnings
from typing import Any, List, Optional, Tuple

from geojson_pydantic import GeometryCollection
from pydantic import Field

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
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
    id: Optional[str] = None
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
    id: Optional[str] = None
    name: str
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    tags: List[Tag] = []
    attributes: List[Attribute] = []
    metadata: List[Metadata] = []
    geometry: Optional[GeometryCollection] = None
    centroid_coordinates: Optional[Tuple[float, float]] = None
    kind: Optional[AssetKind] = None
    actions: Optional[List[ResourceSummary]] = None
    related_to: List[AssetRelationship] = []
    related_from: List[AssetRelationship] = []

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
