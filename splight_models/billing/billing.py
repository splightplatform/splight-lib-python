from pydantic import validator
from ..base import SplightBaseModel
from typing import Optional, Dict
from datetime import datetime

class Billing(SplightBaseModel):
    """
    Billing for a particular kind of activity
    Consists of multiple BillingItem and resumes them in the total_price
    Eg. Deployment of components
    """
    description: str
    items_type: str
    detailed_pricing: Dict = {}
    total_price: float = 0.0

class MonthBilling(SplightBaseModel):
    """
    Billing for a particular month
    Consists of multiple Billing and resumes them in the total_price
    """
    id: Optional[str]
    month: datetime = None
    discount_detail: str = None
    discount_value: float = 0.0
    total_price_without_discount: float = 0.0
    total_price: float = 0.0
    status: Optional[str] = None
    hosted_invoice_url: Optional[str] = None
    invoice_pdf: Optional[str] = None
    paid: bool = False

    @validator('month', pre=True, always=True)
    def set_month_now(cls, v):
        v = v.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return v

    @validator('discount_detail', pre=True, always=True)
    def set_discount_detail(cls, v):
        if not v:
            v = ""
        return v
