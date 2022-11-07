from .base import SplightBaseModel
from typing import Optional


class Mapping(SplightBaseModel):
    id: Optional[str]
    name: Optional[str]
    description: Optional[str] = None
    asset_id: str
    attribute_id: str
    connector_id: Optional[str] = None
    path: Optional[str] = None
    period: Optional[int] = 5000
