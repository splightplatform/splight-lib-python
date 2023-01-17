from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from splight_models.datalake import DatalakeModel


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
    ('Component', 'Component'),
    ('Algorithm', 'Algorithm'),
    ('Connector', 'Connector'),
    ('Network', 'Network'),
)

class SourceType(str, Enum):
    # TODO: Remove this once component types are unified
    component = 'Component'
    algorithm = 'Algorithm'
    network = 'Network'
    connector = 'Connector'


class Notification(DatalakeModel):
    id: Optional[str]
    title: str
    message: str
    seen: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: str = INFO
    source_id: Optional[str]
    source_type: Optional[SourceType] = SourceType.component
