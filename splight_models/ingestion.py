from .base import SplightBaseModel
from typing import Optional
from pydantic import Field
from datetime import datetime,timezone


class Ingestion(SplightBaseModel):
  id: Optional[str]
  asset_id: Optional[str] = None
  name: str
  description: Optional[str] = None
  timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
