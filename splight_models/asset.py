from .base import SplightBaseModel
from typing import List, Optional


class Asset(SplightBaseModel):
    id: Optional[str]
    component_id: Optional[str]
    name: str
    description: Optional[str] = None
    tags: List[str] = []
