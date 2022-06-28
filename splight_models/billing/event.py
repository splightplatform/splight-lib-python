from enum import Enum
from pydantic import validator, root_validator
from ..base import SplightBaseModel
from datetime import datetime, timezone
import pytz

class BillingEventType(str, Enum):
    COMPONENT_DEPLOYMENT = "component_deployment"

class BillingEvent(SplightBaseModel):
    """
    Billing event
    Saved in datalake.
    """
    type: BillingEventType
    event: str #create/destroy
    timestamp: datetime = None
    data: dict = {}

    @validator('timestamp', pre=True, always=True)
    def set_timestamp_now(cls, v):
        if v:
            v = v.replace(tzinfo=pytz.UTC)
            return v
        else:
            return datetime.now(timezone.utc)