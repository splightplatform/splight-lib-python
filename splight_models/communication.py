# TODO move this to splight_models 
from enum import Enum
from typing import Dict, Optional

from splight_models.base import SplightBaseModel
from splight_models.user import User


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
    channel_data: Optional[CommunicationChannelData] = None


class CommunicationClientStatus(str, Enum):
    STOPPED = 'stopped'
    STARTING = 'starting'
    READY = 'ready'
    FAILED = 'failed'
    ERROR =  'error'


class CommunicationTrigger(SplightBaseModel):
    data: Dict
    event_name: str
    instance_id: Optional[str] = None
    socket_id: Optional[str] = None


class CommunicationMessage(SplightBaseModel):
    pass


class CommunicationRPCRequest(CommunicationMessage):
    function: str
    kwargs: Dict = {}
    metadata: Dict = {}


class CommunicationRPCResponse(CommunicationMessage):
    function: str
    kwargs: Dict = {}
    metadata: Dict = {}
    return_value: Optional[str] = None
    error_detail: Optional[str] = None


class CommunicationRPCEvents(str, Enum):
    RPC_REQUEST = 'rpc_request'
    RPC_RESPONSE = 'rpc_response'
