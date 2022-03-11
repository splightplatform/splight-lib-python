from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Notification(BaseModel):
    # TODO: "General" notifications here
    pass


class TriggerNotification(BaseModel):
    trigger_id: str
    update_value: float
    update_timestamp: datetime
    timestamp: Optional[datetime]