from typing import Dict, Any
from splight_models.base import SplightBaseModel
from datetime import datetime, timezone
from pydantic import Field


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
