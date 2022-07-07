from typing import Dict, Any, Literal
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
    user: Dict[str, Any]
    object: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any]
