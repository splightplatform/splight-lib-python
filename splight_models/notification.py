from pydantic import Field
from .base import SplightBaseModel
from datetime import datetime, timezone
from typing import Optional


class Notification(SplightBaseModel):
    id: Optional[str]
    title: str
    message: str
    seen: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
