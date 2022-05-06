from .base import SplightBaseModel
from typing import Optional


class Geopoint(SplightBaseModel):
    id: Optional[str]
    latitude: float
    longitude: float
