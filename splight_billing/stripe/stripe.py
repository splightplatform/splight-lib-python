import stripe
from datetime import datetime
from typing import List, Type, Optional
from pydantic import BaseModel
from .settings import STRIPE_API_KEY
from splight_billing.abstract import AbstractBillingClient
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
            invoice = stripe.Invoice.create(
                customer=self.customer_id,
                collection_method="send_invoice",
                days_until_due=15,
                description=f"Invoice for {instance.month.strftime('%B %Y')} period",
                auto_advance=True,
                metadata={
                    "month": instance.month.isoformat(),
                    "organization_id": self.namespace
                },
                pending_invoice_items_behavior="exclude",
            )
            instance.id = invoice.id
        elif type(instance) == DeploymentBillingItem:
            item = stripe.InvoiceItem.create(
                customer=self.customer_id,
                amount=int(instance.total_price*100),
                currency="usd",
                description=instance.description,
                metadata={
                    "computing_price": int(instance.computing_price*100),
                    "storage_price": int(instance.storage_price*100),
                },
                invoice=instance.month_billing_id
            )
            instance.id = item.id
        return instance

    @validate_resource_type
    def _get(self, resource_type: Type,
             first: bool = False,
             limit_: int = -1,
             skip_: int = 0,
             pending_: bool = False,
             **kwargs) -> List[BaseModel]:
        queryset = []

        if not self.customer_id:
            return None if first else []

        if resource_type == MonthBilling:
            queryset = stripe.Invoice.list(
                customer=self.customer_id
            )
            queryset = [MonthBilling(
                id=invoice.id,
                month=datetime.fromisoformat(invoice.metadata["month"]),
                total_price=invoice.total/100,
                total_price_without_discount=invoice.total/100,
                paid=invoice.paid,
                status=invoice.status,
                hosted_invoice_url=invoice.hosted_invoice_url,
                invoice_pdf=invoice.invoice_pdf,
            ) for invoice in queryset if "month" in invoice.metadata]

        elif resource_type == DeploymentBillingItem:
            # WARNING: Stripe limits by default to 10, max can be 100
            queryset = stripe.InvoiceItem.list(
                customer=self.customer_id,
                pending=pending_,
            )
            queryset = [DeploymentBillingItem(
                id=item.id,
                description=item.description,
                computing_price=float(item.metadata.get("computing_price", 0))/100,
                storage_price=float(item.metadata.get("storage_price", 0))/100,
                total_price=item.amount/100,
            ) for item in queryset]

        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)

        if limit_ != -1:
            queryset = queryset[skip_:skip_ + limit_]
        if first:
            return queryset[0] if queryset else None
        return queryset


    @validate_resource_type
    def delete(self, resource_type: Type, id: str):
        if resource_type == MonthBilling:
            stripe.Invoice.delete(id)
        elif resource_type == DeploymentBillingItem:
            stripe.InvoiceItem.delete(id)