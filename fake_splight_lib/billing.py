import uuid
from collections import defaultdict
from typing import List, Type, Dict
from pydantic import BaseModel
from splight_billing.abstract import AbstractBillingClient
from splight_models import MonthBilling, DeploymentBillingItem
from client import validate_instance_type, validate_resource_type
from splight_lib.logging import getLogger
logger = getLogger()


class FakeBillingClient(AbstractBillingClient):
    valid_classes = [MonthBilling, DeploymentBillingItem]

    database : Dict[Type, List] = defaultdict(lambda : [])

    def __init__(self, namespace="default", customer_id="default", *args, **kwargs):
        super().__init__(namespace, *args, **kwargs)
        self.customer_id=customer_id

    @validate_instance_type
    def save(self, instance: BaseModel) -> BaseModel:
        logger.debug(f"[FAKED] Executing save with {type(instance)}")
        if type(instance) == MonthBilling:
            fake_id = "in_" + str(uuid.uuid4())
            fake_invoice_pdf = "https://fakeurl.com/abc.pdf"
            fake_hosted_invoice_url = "https://fakehost.com/pay"
            instance.id = fake_id
            instance.invoice_pdf = fake_invoice_pdf
            instance.hosted_invoice_url = fake_hosted_invoice_url
            self.database[MonthBilling].append(instance)
        elif type(instance) == DeploymentBillingItem:
            fake_id = "ii_" + str(uuid.uuid4())
            instance.id = fake_id
        return instance

    @validate_resource_type
    def _get(self, resource_type: Type,
             first: bool = False,
             limit_: int = -1,
             skip_: int = 0,
             pending_: bool = False,
             **kwargs) -> List[BaseModel]:
        queryset = []
        logger.debug(f"[FAKED] Executing get with {resource_type}")

        if not self.customer_id or pending_:
            return None if first else []

        queryset = self.database[resource_type]

        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)

        if limit_ != -1:
            queryset = queryset[skip_:skip_ + limit_]
        if first:
            return queryset[0] if queryset else None
        return queryset


    @validate_resource_type
    def delete(self, resource_type: Type, id: str):
        logger.debug(f"[FAKED] Executing delete with {resource_type} {id}")

        queryset = self.database.get(resource_type, [])
        for i, item in enumerate(queryset):
            if item.id == id:
                del queryset[i]
                return