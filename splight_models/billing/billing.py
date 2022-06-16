import os
from enum import Enum
from pydantic import validator, root_validator
from ..base import SplightBaseModel
from typing import List, Optional, Dict
from datetime import datetime

class BillingEventType(str, Enum):
    COMPONENT_DEPLOYMENT = "component_deployment"

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
            if v < 0 or values > 100:
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
        return v or datetime.now()

class BillingSettings(SplightBaseModel):
    """
    Global billing settings
    Updated through the time in order to recreate past billings
    Saved in database
    """
    id: Optional[str]
    timestamp: datetime = None
    pricing: Pricing = Pricing()
    discounts: List[Discount] = []
    computing_time_measurement_per_hour: bool = False

    @validator('timestamp', pre=True, always=True)
    def set_timestamp_now(cls, v):
        return v or datetime.now()

class BillingItem(SplightBaseModel):
    """
    A billing item is a line item in the billing report.
    Created considering BillingEvents.
    Eg. DeploymentBillingItems
    """
    description: str = "Default"
    total_price: float = None

class Billing(SplightBaseModel):
    """
    Billing for a particular kind of activity
    Eg. Deployment of components
    """
    description: str
    items: List[BillingItem] = []
    detailed_pricing: Dict = {}
    total_price: float = None

    @root_validator(pre=True)
    def set_total_price(cls, values):
        total_price = 0
        for item in values['items']:
            if type(item) != dict:
                item = item.dict()
                total_price += item['total_price']
        total_price = max(0, total_price)
        values['total_price'] = total_price
        return values

    @root_validator(pre=True)
    def set_detailed_pricing(cls, values):
        items = values['items']
        detailed_pricing = {}
        for item in items:
            if type(item) != dict:
                item = item.dict()
            for field, _ in item.items():
                if field in BillingItem.__fields__:
                    continue
                if field not in detailed_pricing:
                    detailed_pricing[field] = 0
                detailed_pricing[field] = detailed_pricing[field] + item[field]
        values['detailed_pricing'] = detailed_pricing
        return values

class MonthBilling(SplightBaseModel):
    id: Optional[str]
    month: datetime = None
    billings: List[Billing] = []
    discount: Optional[Discount] = None
    discount_value: float = 0
    total_price_without_discount: float = None
    total_price: float = None
    paid: bool = False

    @validator('month', pre=True, always=True)
    def set_month_now(cls, v):
        if v:
            v = v.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return v
        now = datetime.now()
        return datetime(now.year, now.month, 1)

    @root_validator(pre=True)
    def set_total_price(cls, values):
        billings = values['billings']
        discount = values['discount']
        if not discount:
            discount = 0
        else:
            discount = discount.dict()
            discount = discount["value"] if discount["type"] == DiscountType.FIXED else billing_value * discount["value"] / 100
        discount = max(0, discount)

        billing_value = 0
        for billing in billings:
            if type(billing) != dict:
                billing = billing.dict()
            billing_value += billing["total_price"]

        billing_value = max(0, billing_value)
        total_price = max(0, billing_value - discount)

        values['total_price_without_discount'] = billing_value
        values['total_price'] = total_price
        values['discount_value'] = discount
        return values


# Create billing item types here
# DEPLOYMENT
class DeploymentBillingItem(BillingItem):
    computing_price: float = 0
    storage_price: float = 0

    @root_validator(pre=True)
    def set_total_price(cls, values):
        values['total_price'] = max(0, values['computing_price'] + values['storage_price'])
        return values