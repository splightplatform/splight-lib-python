from .base import SplightBaseModel
from typing import Optional, Dict


class Namespace(SplightBaseModel):
    id: Optional[str]
    environment: Dict = {}
