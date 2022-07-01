from pydantic import Field
from .base import SplightBaseModel
from datetime import datetime, timezone
from typing import Optional
from .severity import SeverityType
from enum import Enum


class SourceType(str, Enum):
    algorithm = 'Algorithm'
    network = 'Network'
    connector = 'Connector'


class Notification(SplightBaseModel):
    id: Optional[str]
    title: str
    message: str
    seen: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: SeverityType = SeverityType.info
    asset_id: Optional[str]
    attribute_id: Optional[str]
    rule_id: Optional[str]
    source_id: Optional[str]
    source_type: Optional[SourceType]
