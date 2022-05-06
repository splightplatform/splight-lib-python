from .base import SplightBaseModel
from typing import Optional


class Tag(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
