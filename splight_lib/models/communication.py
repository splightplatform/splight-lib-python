from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel


class CommunicationChannelData(BaseModel):
    user_id: str
    user_info: Dict

    # TODO: Review following method
    # @classmethod
    # def parse_from_user(cls, user: User):
    #     return cls.parse_obj(
    #         {"user_id": user.user_id, "user_info": user.dict()}
    #     )


class CommunicationContext(BaseModel):
    auth_headers: Optional[Dict] = None
    auth_endpoint: Optional[str] = None
    key: str
    channel: str
    private_room_channel: str
    presence_room_channel: str
    channel_data: Optional[CommunicationChannelData] = None


class CommunicationClientStatus(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    READY = "ready"
    FAILED = "failed"
    ERROR = "error"
