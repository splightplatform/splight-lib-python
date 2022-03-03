from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Notification(BaseModel):
    id: Optional[str]
    trigger_id: str
    priority: str
    message: str
    value: float
    update_timestamp: datetime