from typing import Dict, Any
from .datalake import DatalakeModel


class UserActivityType:
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"


class UserActivity(DatalakeModel):
    action: str
    user: Dict[str, Any]
    object: Dict[str, Any]
    details: Dict[str, Any]
