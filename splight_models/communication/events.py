
from enum import Enum
from typing import Dict, Optional
from pydantic import Field
from splight_models.base import SplightBaseModel
from splight_models.communication import Operation
from splight_models.mapping import Mapping
from splight_models.rule import Rule
from splight_models.user import User
from datetime import datetime, timezone


class EventNames(str, Enum):
    OPERATION_TRIGGER = 'operation-trigger'
    OPERATION_CREATE = 'operation-create'
    OPERATION_UPDATE = 'operation-update'
    MAPPING_CREATE = "mapping-create"
    MAPPING_DELETE = "mapping-delete"
    RULE_CREATE = 'rule-create'
    RULE_DELETE = 'rule-delete'


class CommunicationEvent(SplightBaseModel):
    event_name: str
    id: Optional[str] = None
    instance_id: Optional[str] = None
    socket_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))  # pusher cannot json serialize datetime objects
    display_text: Optional[str] = None
    user: Optional[User] = None
    data: Dict


class OperationTriggerEvent(CommunicationEvent):
    event_name: str = Field(EventNames.OPERATION_TRIGGER, const=True)
    data: Operation


class OperationCreateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.OPERATION_CREATE, const=True)
    data: Operation


class OperationUpdateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.OPERATION_UPDATE, const=True)
    data: Operation


class MappingCreateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.MAPPING_CREATE, const=True)
    data: Mapping


class MappingDeleteEvent(CommunicationEvent):
    event_name: str = Field(EventNames.MAPPING_DELETE, const=True)
    data: Mapping


class RuleCreateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.RULE_CREATE, const=True)
    data: Rule


class RuleDeleteEvent(CommunicationEvent):
    event_name: str = Field(EventNames.RULE_DELETE, const=True)
    data: Rule
