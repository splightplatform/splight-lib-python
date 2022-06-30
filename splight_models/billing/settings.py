from enum import Enum
from pydantic import validator, root_validator
from ..base import SplightBaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import pytz

class DiscountType(str, Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"

class Discount(SplightBaseModel):
    organization_id: str
    type: DiscountType
    value: float

    @root_validator(pre=True)
    def check_discount_value(cls, values):
        v = values['value']
        if values['type'] == DiscountType.PERCENTAGE:
            if v < 0 or v > 100:
                raise ValueError("Discount percentage must be between 0 and 100")
        return values

class Pricing(SplightBaseModel):
    COMPUTING_PRICE_PER_HOUR: float = 0.04
    STORAGE_PRICE_PER_GB: float = 2
    IMPACT_MULTIPLIER: Dict[str, float] = {
        "1": 10,
        "2": 25,
        "3": 63,
        "4": 156,
        "5": 391,
    }

class BillingSettings(SplightBaseModel):
    """
    Global billing settings
    Updated through the time in order to recreate past billings
    Saved in database "default" namespace
    """
    id: Optional[str]
    timestamp: datetime = None
    pricing: Pricing = Pricing()
    discounts: List[Discount] = []
    computing_time_measurement_per_hour: bool = True

    @validator('timestamp', pre=True, always=True)
    def set_timestamp_now(cls, v):
        if v:
            v = v.replace(tzinfo=pytz.UTC)
            return v
        else:
            return datetime.now(timezone.utc)