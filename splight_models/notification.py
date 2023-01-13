from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from splight_models.datalake import DatalakeModel


class SourceType(str, Enum):
    component = 'Component'
    system = 'System'
    organization = 'Organization'
    user = 'User'

class TargetType(str, Enum):
    component = 'Component'
    organization = 'Organization'
    asset = 'Asset'
    attribute = 'Attribute'
    file_ = 'File'
    graph = 'Graph'
    query = 'Query'
    user = 'User'


class Notification(DatalakeModel):
    id: Optional[str]
    message: str
    seen: bool = False
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_id: Optional[str]
    source_type: Optional[SourceType] = SourceType.component
    target_id: Optional[str]
    target_type: Optional[TargetType] = TargetType.component
    is_error: bool = False
    external_url: Optional[str]
    volatile: bool = False
