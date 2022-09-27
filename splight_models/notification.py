from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from splight_models.base import SplightBaseModel
from splight_models.datalake import DatalakeModel
from splight_models.severity import SeverityType
from splight_models.user import User


SYSTEM = 'system'
INFO = 'info'
LOW = 'low'
MEDIUM = 'medium'
HIGH = 'high'
CRITICAL = 'critical'

GREATER_THAN = 'gt'
GREATER_THAN_OR_EQUAL = 'ge'
LOWER_THAN = 'lt'
LOWER_THAN_OR_EQUAL = 'le'
EQUAL = 'eq'

SEVERITIES = (
    (SYSTEM, 'system'),
    (INFO, 'info'),
    (LOW, 'low'),
    (MEDIUM, 'medium'),
    (HIGH, 'high'),
    (CRITICAL, 'critical'),
)

SOURCE_TYPE = (
    ('Algorithm', 'Algorithm'),
    ('Network', 'Network'),
    ('Connector', 'Connector'),
)


class SourceType(str, Enum):
    algorithm = 'Algorithm'
    network = 'Network'
    connector = 'Connector'


class Notification(DatalakeModel):
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


class NotificationUserData(SplightBaseModel):
    user_id: str
    user_info: User

    @classmethod
    def parse_from_user(cls, user: User):
        return cls.parse_obj(
            {"user_id": user.user_id, "user_info": user}
        )


class NotificationContext(SplightBaseModel):
    auth_endpoint: Optional[str] = None
    key: str
    channel: str
