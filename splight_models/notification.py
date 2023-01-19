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
    dashboard = 'Dashboard'
    asset = 'Asset'
    attribute = 'Attribute'
    file_ = 'File'
    graph = 'Graph'
    query = 'Query'

class Notification(DatalakeModel):
    id: Optional[str]
    message: str
    seen: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notify_by_email: bool = False
    notify_by_web: bool = False
    notify_by_sms: bool = False
    notify_by_push: bool = False
    source_id: Optional[str]
    source_type: Optional[SourceType] = SourceType.component
    target_id: Optional[str]
    target_type: Optional[TargetType] = TargetType.component
    volatile: bool = False
    redirect_url: Optional[str]
