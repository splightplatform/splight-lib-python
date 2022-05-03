from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional


class Notification(BaseModel):
    id: Optional[str]
    title: str
    message: str
    seen: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
