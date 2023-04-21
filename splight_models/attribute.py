from typing import Optional

from .base import SplightBaseModel


class Attribute(SplightBaseModel):
    id: Optional[str]
    name: str
