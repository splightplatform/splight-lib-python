from .base import SplightBaseModel
from typing import Optional


class Mapping(SplightBaseModel):
    id: Optional[str]
    name: Optional[str]
    description: Optional[str] = None
    asset_id: str
    attribute_id: str
    output_format: str
