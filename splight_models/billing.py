from .base import SplightBaseModel
from typing import Optional, Dict
from enum import Enum
from pydantic import validator
from datetime import datetime, timezone
import pytz

class InvoiceMetadata(SplightBaseModel):
    month: Optional[datetime]
    organization_id: Optional[str]

class Invoice(SplightBaseModel):
    id: Optional[str]
    customer: str
    metadata: Optional[InvoiceMetadata]
    total: float
    paid: bool
    status: str
    hosted_invoice_url: Optional[str]
    invoice_pdf: Optional[str]

class InvoiceItem(SplightBaseModel):
    id: Optional[str]
    customer: str
    amount: int
    currency: str
    description: str
    metadata: Dict
    invoice: str

class Coupon(SplightBaseModel):
    amount_off: Optional[int]
    percent_off: Optional[int]

class Discount(SplightBaseModel):
    coupon: Coupon

class Customer(SplightBaseModel):
    id: Optional[str]
    currency: Optional[str]
    balance: int
    discount: Optional[Discount]

class CustomerPortal(SplightBaseModel):
    customer: str
    url: str


# TODO: Remove billing event
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
