import uuid
from .base import SplightBaseModel
from typing import List, Optional
from datetime import datetime

class BillingEvent(SplightBaseModel):
    id: Optional[str]
    component_id: str #aka external_id
    impact: int
    type: str
    timestamp: Optional[datetime]
