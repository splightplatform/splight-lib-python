from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from splight_models import SplightBaseModel


class SourceType(str, Enum):
    component = 'Component'
    system = 'System'
    user = 'User'


class TargetType(str, Enum):
    component = 'Component'
    dashboard = 'Dashboard'
    asset = 'Asset'
    attribute = 'Attribute'
    file_ = 'File'
    graph = 'Graph'
    query = 'Query'


class Notification(SplightBaseModel):
    id: Optional[str]
    message: str
    seen: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    notify_by_email: Optional[bool] = False
    notify_by_web: Optional[bool] = True
    notify_by_sms: Optional[bool] = False
    notify_by_push: Optional[bool] = True
    source_id: Optional[str] = None
    source_type: Optional[SourceType] = None
    target_id: Optional[str] = None
    target_type: Optional[TargetType] = None
    volatile: bool = False
    redirect_url: Optional[str]
