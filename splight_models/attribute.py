from .base import SplightBaseModel
from typing import Optional


class Attribute(SplightBaseModel):
    id: Optional[str]
    name: str
