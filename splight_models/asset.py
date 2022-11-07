from .base import SplightBaseModel
from typing import List, Optional


class Asset(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    external_id: Optional[str]
    tags: List[str] = []
