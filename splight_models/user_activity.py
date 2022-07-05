from typing import Dict, Any
from .base import SplightBaseModel
from datetime import datetime, timezone
from pydantic import Field
from enum import Enum


class UserActivityType:
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"


class UserActivity(SplightBaseModel):
    action: str
    email: str  # is this enough to uniquely identify a user?
    target_type: str
    target_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any]
