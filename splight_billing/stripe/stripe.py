import stripe
from splight_billing.abstract import AbstractBillingClient
from typing import List, Type
from pydantic import BaseModel
from .settings import STRIPE_API_KEY
from splight_models import MonthBilling, DeploymentBillingItem
from client import validate_instance_type, validate_resource_type

stripe.api_key = STRIPE_API_KEY

class StripeClient(AbstractBillingClient):
    valid_classes = [MonthBilling, DeploymentBillingItem]

    def __init__(self, namespace="default", customer_id="default", *args, **kwargs):
        super().__init__(namespace, *args, **kwargs)
        self.customer_id=customer_id

    @validate_instance_type
    def save(self, instance: BaseModel) -> BaseModel:
        if type(instance) == MonthBilling:
            stripe.Invoice.create(
                customer=self.customer_id,
                collection_method="send_invoice",
            )
        elif type(instance) == DeploymentBillingItem:
            stripe.InvoiceItem.create(
                customer=self.customer_id,
                amount=int(instance.total_price*100),
                currency="usd",
                description=instance.description,
                metadata={
                    "computing_price": int(instance.computing_price*100),
                    "storage_price": int(instance.storage_price*100),
                }
            )
    @validate_resource_type
    def _get(self, resource_type: Type,
             first: bool = False,
             limit_: int = -1,
             skip_: int = 0,
             **kwargs) -> List[BaseModel]:
        pass