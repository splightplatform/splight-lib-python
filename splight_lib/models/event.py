from datetime import datetime, timezone
from enum import auto
from typing import Dict, Optional

from pydantic import BaseModel, Field
from splight_lib.models.component import Command
from splight_lib.models.setpoint import SetPoint
from strenum import (
    KebabCaseStrEnum,
    LowercaseStrEnum,
    PascalCaseStrEnum,
    SnakeCaseStrEnum,
    UppercaseStrEnum,
)


class EventActions(UppercaseStrEnum):
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()
    TRIGGER = auto()
    READ = auto()


class EventNames(KebabCaseStrEnum):
    # TODO make this use EventActions.
    COMPONENTCOMMAND_TRIGGER = auto()
    COMPONENTCOMMAND_CREATE = auto()
    COMPONENTCOMMAND_UPDATE = auto()
    # TODO add Asset Attribute and all shared objects

    SETPOINT_CREATE = auto()
    SETPOINT_UPDATE = auto()


class ComponentCommandStatus(SnakeCaseStrEnum):
    NOT_SENT = auto()
    PENDING = auto()
    SUCCESS = auto()
    ERROR = auto()


class ComponentCommandResponse(BaseModel):
    return_value: Optional[str]
    error_detail: Optional[str]


class CommunicationEvent(BaseModel):
    event_name: str
    id: Optional[str] = None
    instance_id: Optional[str] = None
    socket_id: Optional[str] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
    )  # pusher cannot json serialize datetime objects
    display_text: Optional[str] = None
    data: Dict


class ComponentCommand(BaseModel):
    id: Optional[str]
    command: Command
    status: ComponentCommandStatus
    response: ComponentCommandResponse = ComponentCommandResponse()

    def get_event_name(self, action: EventActions) -> str:
        return f"componentcommand_{action}"


class ComponentCommandTriggerEvent(CommunicationEvent):
    event_name: str = Field(EventNames.COMPONENTCOMMAND_TRIGGER, const=True)
    data: ComponentCommand


class ComponentCommandCreateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.COMPONENTCOMMAND_CREATE, const=True)
    data: ComponentCommand


class ComponentCommandUpdateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.COMPONENTCOMMAND_UPDATE, const=True)
    data: ComponentCommand


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


class SetPointResponse(BaseModel):
    id: Optional[str]
    component: str
    status: SetPointResponseStatus
    created_at: Optional[datetime] = None


class SetPointCreateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.SETPOINT_CREATE, const=True)
    data: SetPoint


class SetPointUpdateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.SETPOINT_UPDATE, const=True)
    data: SetPoint
