# TODO move this to splight_models 
from enum import Enum
from typing import Dict, Optional

from splight_models.base import SplightBaseModel
from splight_models.user import User

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
    ERROR =  'error'


class CommunicationEvent(SplightBaseModel):
    event_name: str
    instance_id: Optional[str] = None
    socket_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")) # pusher cannot json serialize datetime objects
    display_text: Optional[str] = None
    data: Dict

class CommunicationRPCRequest(SplightBaseModel):
    function: str
    kwargs: Dict = {}
    metadata: Dict = {}


class CommunicationRPCResponse(SplightBaseModel):
    function: str
    kwargs: Dict = {}
    metadata: Dict = {}
    return_value: Optional[str] = None
    error_detail: Optional[str] = None


class CommunicationRPCEvents(str, Enum):
    RPC_REQUEST = 'rpc_request'
    RPC_RESPONSE = 'rpc_response'


class CommunicationRPCRequestEvent(CommunicationEvent):
    event_name: str = CommunicationRPCEvents.RPC_REQUEST
    data: CommunicationRPCRequest


class CommunicationRPCResponseEvent(CommunicationEvent):
    event_name: str = CommunicationRPCEvents.RPC_RESPONSE
    data: CommunicationRPCResponse
