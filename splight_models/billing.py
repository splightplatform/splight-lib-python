import os
from enum import Enum
from pydantic import validator
from .base import SplightBaseModel
from typing import List, Optional
from datetime import datetime

class BillingEventType(str, Enum):
    COMPONENT_DEPLOYMENT = "component_deployment"

class BillingEvent(SplightBaseModel):
    type: BillingEventType
    event: str #create/destroy
    timestamp: datetime = None
    data: dict = {}

    @validator('timestamp', pre=True, always=True)
    def set_timestamp_now(cls, v):
        return v or datetime.now()

