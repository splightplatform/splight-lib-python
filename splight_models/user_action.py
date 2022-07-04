from typing import Dict
from .base import SplightBaseModel
from datetime import datetime, timezone
from pydantic import Field
from enum import Enum


class UserActionType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class UserAction(SplightBaseModel):
    action: UserActionType
    username: str  # is this enough to uniquely identify a user?
    email: str
    target_type: str
    target_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, str]
