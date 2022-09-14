from pydantic import BaseModel
from typing import List, Type, Dict
from abc import ABC, abstractmethod, abstractproperty
from splight_abstract.client import AbstractClient, QuerySet


class AbstractBillingSubClient(AbstractClient):
    @abstractmethod
    def create(self, *args, **kwargs) -> BaseModel:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)
    
    @abstractmethod
    def _get(self, first=False, limit_: int = -1, skip_: int = 0, *args, **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass

class AbstractBillingClient(ABC):
    @abstractproperty
    def invoice(self) -> AbstractBillingSubClient:
        pass

    @abstractproperty
    def invoice_item(self) -> AbstractBillingSubClient:
        pass

    @abstractproperty
    def customer(self) -> AbstractBillingSubClient:
        pass

    @abstractproperty
    def customer_portal(self) -> AbstractBillingSubClient:
        pass