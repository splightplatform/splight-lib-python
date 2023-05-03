from typing import List, Optional, Tuple

from geojson_pydantic import GeometryCollection

from .attribute import Attribute
from .base import SplightBaseModel


class Asset(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    external_id: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    tags: List[str] = []
    attributes: List[Attribute] = []
    verified: bool = False
    geometry: Optional[GeometryCollection]
    centroid_coordinates: Optional[Tuple[float, float]]
