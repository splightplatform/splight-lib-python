import warnings
from typing import Any, List, Optional, Tuple

from geojson_pydantic import GeometryCollection
from pydantic import Field

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.attribute import Attribute
from splight_lib.models.base import SplightDatabaseBaseModel
from splight_lib.models.metadata import Metadata

warnings.filterwarnings("ignore", category=UserWarning)


class Asset(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    tags: List[str] = []
    attributes: List[Attribute] = []
    metadata: List[Metadata] = []
    geometry: Optional[GeometryCollection] = None
    centroid_coordinates: Optional[Tuple[float, float]] = None

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
