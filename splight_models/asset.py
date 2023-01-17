from .base import SplightBaseModel
from typing import List, Optional
from .attribute import Attribute


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
