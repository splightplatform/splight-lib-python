
from enum import Enum
from typing import Dict, Optional
from pydantic import Field
from splight_models.base import SplightBaseModel
from splight_models.user import User
from datetime import datetime, timezone


class EventActions(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    TRIGGER = "TRIGGER"
    READ = "READ"


class EventNames(str, Enum):
    # TODO make this use EventActions.
    COMPONENT_COMMAND_TRIGGER = 'componentcommand-trigger'
    COMPONENT_COMMAND_CREATE = 'componentcommand-create'
    COMPONENT_COMMAND_UPDATE = 'componentcommand-update'
    # TODO add Asset Attribute and all shared objects

    SETPOINT_CREATE = 'setpoint-create'
    SETPOINT_UPDATE = 'setpoint-update'


class CommunicationEvent(SplightBaseModel):
    event_name: str
    id: Optional[str] = None
    instance_id: Optional[str] = None
    socket_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))  # pusher cannot json serialize datetime objects
    display_text: Optional[str] = None
    user: Optional[User] = None
    data: Dict
