# TODO move this to splight_models
from enum import Enum
from typing import Dict, Optional

from splight_models.base import SplightBaseModel
from splight_models.user import User
from splight_models.mapping import ClientMapping
from splight_models.rule import MappingRule

from pydantic import Field
from datetime import datetime, timezone


class CommunicationChannelData(SplightBaseModel):
    user_id: str
    user_info: Dict

    @classmethod
    def parse_from_user(cls, user: User):
        return cls.parse_obj(
            {
                "user_id": user.user_id,
                "user_info": user.dict()
            }
        )


class CommunicationContext(SplightBaseModel):
    auth_headers: Optional[Dict] = None
    auth_endpoint: Optional[str] = None
    key: str
    channel: str
    presence_room_channel: str
    channel_data: Optional[CommunicationChannelData] = None


class CommunicationClientStatus(str, Enum):
    STOPPED = 'stopped'
    STARTING = 'starting'
    READY = 'ready'
    FAILED = 'failed'
    ERROR = 'error'


class CommunicationEvent(SplightBaseModel):
    event_name: str
    id: Optional[str] = None
    instance_id: Optional[str] = None
    socket_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))  # pusher cannot json serialize datetime objects
    display_text: Optional[str] = None
    user: Optional[User] = None
    data: Dict


class OperationRequest(SplightBaseModel):
    function: str
    kwargs: Dict = {}
    metadata: Dict = {}


class OperationResponse(SplightBaseModel):
    function: str
    kwargs: Dict = {}
    metadata: Dict = {}
    return_value: Optional[str] = None
    error_detail: Optional[str] = None


class OperationEvents(str, Enum):
    OPERATION_REQUEST = 'operation-request'
    OPERATION_RESPONSE = 'operation-response'


class OperationRequestEvent(CommunicationEvent):
    event_name: str = OperationEvents.OPERATION_REQUEST
    data: OperationRequest


class OperationResponseEvent(CommunicationEvent):
    event_name: str = OperationEvents.OPERATION_RESPONSE
    data: OperationResponse


class MappingEvents(str, Enum):
    MAPPING_CREATE = "mapping-create"
    MAPPING_DELETE = "mapping-delete"


class MappingCreateEvent(CommunicationEvent):
    event_name: str = Field(MappingEvents.MAPPING_CREATE, const=True)
    data: ClientMapping


class MappingDeleteEvent(CommunicationEvent):
    event_name: str = Field(MappingEvents.MAPPING_DELETE, const=True)
    data: ClientMapping


class RuleEvents(str, Enum):
    RULE_CREATE = 'rule-create'
    RULE_DELETE = 'rule-delete'


class RuleCreateEvent(CommunicationEvent):
    event_name: str = Field(RuleEvents.RULE_CREATE, const=True)
    data: MappingRule


class RuleDeleteEvent(CommunicationEvent):
    event_name: str = Field(RuleEvents.RULE_DELETE, const=True)
    data: MappingRule
