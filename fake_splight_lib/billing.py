from typing import List, Type

from pydantic import BaseModel

from splight_abstract import AbstractBillingClient, AbstractBillingSubClient
from splight_lib import logging
from splight_models import Customer, CustomerPortal, Invoice, InvoiceItem

logger = logging.getLogger()


class FakeBillingSubClient(AbstractBillingSubClient):
    def __init__(self, type: Type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = type

    database = {
        Invoice: [],
        InvoiceItem: [],
        Customer: [],
        CustomerPortal: [],
    }

    def create(self, *args, **kwargs) -> BaseModel:
        logger.debug("[FAKED] Created object")
        kwargs["currency"] = "USD"
        kwargs["balance"] = 0
        kwargs["id"] = "cus_MLC93GFYmg2oTZ"
        object = self.type.parse_obj(kwargs)
        self.database[self.type].append(object)
        return object

    def _get(
        self, first=False, limit_: int = -1, skip_: int = 0, *args, **kwargs
    ) -> List[BaseModel]:
        queryset = self.database[self.type]
        kwargs = self._validated_kwargs(
            self.class_map[self.stripe_type], **kwargs
        )
        queryset = self._filter(queryset, **kwargs)
        if limit_ != -1:
            queryset = queryset[skip_:skip_ + limit_]
        if first:
            return queryset[0] if queryset else None
        return queryset

    def retrieve(self, id: str) -> BaseModel:
        for item in self.database[self.type]:
            if item.id == id:
                return item
        return None

    def delete(self, id: str) -> None:
        for item in self.database[self.type]:
            if item.id == id:
                self.database[self.type].remove(item)
                break


class FakeBillingClient(AbstractBillingClient):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._invoice = FakeBillingSubClient(Invoice)
        self._invoice_item = FakeBillingSubClient(InvoiceItem)
        self._customer = FakeBillingSubClient(Customer)
        self._customer_portal = FakeBillingSubClient(CustomerPortal)

    @property
    def invoice(self) -> AbstractBillingSubClient:
        return self._invoice

    @property
    def invoice_item(self) -> AbstractBillingSubClient:
        return self._invoice_item

    @property
    def customer(self) -> AbstractBillingSubClient:
        return self._customer

    @property
    def customer_portal(self) -> AbstractBillingSubClient:
        return self._customer_portal
