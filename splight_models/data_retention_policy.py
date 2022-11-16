from .base import SplightBaseModel
from typing import Any, Dict, Optional


class DataRetentionPolicy(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    namespace: str
    filter_params: Dict[str, Any] = {}
    months: Optional[int]
