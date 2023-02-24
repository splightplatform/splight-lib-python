from splight_models import EventNames, CommunicationEvent
from pydantic import Field, validator, ValidationError
from typing import Union, Optional, List
from .base import SplightBaseModel
from datetime import datetime
from enum import auto
from strenum import PascalCaseStrEnum, LowercaseStrEnum


class SetPointType(PascalCaseStrEnum):
    Number = auto()
    String = auto()
    Boolean = auto()

    def __str__(self):
        return self.value


class SetPointResponseStatus(LowercaseStrEnum):
    SUCCESS = auto()
    ERROR = auto()
    IGNORE = auto()

    def __str__(self):
        return self.value


class SetPointResponse(SplightBaseModel):
    id: Optional[str]
    component: str
    status: SetPointResponseStatus
    created_at: Optional[datetime] = None


class SetPoint(SplightBaseModel):
    id: Optional[str]
    asset: str
    attribute: str
    type: SetPointType
    value: Union[str, bool, float]
    responses: List[SetPointResponse] = []

    @validator('value')
    def cast_value(cls, v, values, **kwargs):
        if not "type" in values:
            raise ValueError("type is required")

        if values["type"] == SetPointType.Number:
            try:
                return float(v)
            except ValueError:
                raise ValidationError("value must be a number")

        if values["type"] == SetPointType.Boolean:
            try:
                return bool(v)
            except ValueError:
                raise ValidationError("value must be a boolean")

        if values["type"] == SetPointType.String:
            return str(v)


class SetPointCreateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.SETPOINT_CREATE, const=True)
    data: SetPoint


class SetPointUpdateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.SETPOINT_UPDATE, const=True)
    data: SetPoint
