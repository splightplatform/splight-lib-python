from typing import List, Optional

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
