from splight_models import EventNames, CommunicationEvent
from pydantic import Field
from typing import Union, Optional, List
from enum import Enum
from .base import SplightBaseModel
from datetime import datetime


class SetPointType(str, Enum):
    Number = "Number"
    Stringh = "String"
    Boolean = "Boolean"

    def __str__(self):
        return self.value


class SetPointResponseStatus(str, Enum):
    SUCCESS = "succeeded"
    ERROR = "error"
    IGNORE = "ignore"

    def __str__(self):
        return self.value


class SetPointResponse(SplightBaseModel):
    id: Optional[str]
    component: str
    status: SetPointResponseStatus
    created_date: Optional[datetime] = None


class SetPoint(SplightBaseModel):
    id: Optional[str]
    asset: str
    attribute: str
    type: SetPointType
    value: Union[int, float, str, bool]
    responses: List[SetPointResponse] = []
    created_date: Optional[datetime] = None


class SetPointCreateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.SETPOINT_CREATE, const=True)
    data: SetPoint


class SetPointUpdateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.SETPOINT_UPDATE, const=True)
    data: SetPoint
