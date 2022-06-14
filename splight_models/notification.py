from pydantic import Field
from .base import SplightBaseModel
from datetime import datetime, timezone
from typing import Optional
from .common import SeverityType


class Notification(SplightBaseModel):
    id: Optional[str]
    title: str
    message: str
    seen: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: SeverityType = SeverityType.info
    asset_id: str
    attribute_id: str
    rule_id: str
    source_id: str
    source_type: str
