from datetime import datetime, timezone
from enum import auto
from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field
from strenum import KebabCaseStrEnum, SnakeCaseStrEnum, UppercaseStrEnum

from splight_lib.models.component import Command


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
    return_value: Optional[str] = None
    error_detail: Optional[str] = None


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
    id: Optional[str] = None
    command: Command
    status: ComponentCommandStatus
    response: ComponentCommandResponse = ComponentCommandResponse()

    def get_event_name(self, action: EventActions) -> str:
        return f"componentcommand_{action}"


class ComponentCommandTriggerEvent(CommunicationEvent):
    event_name: Literal[
        EventNames.COMPONENTCOMMAND_TRIGGER
    ] = EventNames.COMPONENTCOMMAND_TRIGGER
    data: ComponentCommand


class ComponentCommandCreateEvent(CommunicationEvent):
    event_name: Literal[
        EventNames.COMPONENTCOMMAND_CREATE
    ] = EventNames.COMPONENTCOMMAND_CREATE
    data: ComponentCommand


class ComponentCommandUpdateEvent(CommunicationEvent):
    event_name: Literal[
        EventNames.COMPONENTCOMMAND_UPDATE
    ] = EventNames.COMPONENTCOMMAND_UPDATE
    data: ComponentCommand
