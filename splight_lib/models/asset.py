from typing import Any, List, Optional, Tuple

from geojson_pydantic import GeometryCollection
from splight_lib.models.attribute import Attribute
from splight_lib.models.base import SplightDatabaseBaseModel


class Asset(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    latitude: Optional[float]
    longitude: Optional[float]
    tags: List[str] = []
    attributes: List[Attribute] = []
    verified: bool = False
    geometry: Optional[GeometryCollection]
    centroid_coordinates: Optional[Tuple[float, float]]

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
