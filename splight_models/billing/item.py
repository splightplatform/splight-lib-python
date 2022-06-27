from ..base import SplightBaseModel
from typing import Optional

class BillingItem(SplightBaseModel):
    """
    A billing item is a line item in the billing report.
    Corresponds to one Billing
    Created considering BillingEvents.
    Eg. DeploymentBillingItems
    """
    id: Optional[str]
    billing_id: Optional[str]
    description: str = "Default description"
    total_price: float = 0.0

#Types:

# DEPLOYMENT
class DeploymentBillingItem(BillingItem):
    computing_price: float = 0
    storage_price: float = 0