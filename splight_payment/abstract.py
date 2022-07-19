from client import AbstractClient
from abc import abstractmethod

class AbstractPaymentClient(AbstractClient):

    def __init__(self, namespace="default", customer_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @staticmethod
    def create_customer(self, name: str, city: str, country: str, postal_code: str, email: str):
        pass

    @abstractmethod
    def add_item(self, description: str, price: float):
        pass
    
    @abstractmethod
    def close(self):
        pass
    
    @abstractmethod 
    def add_card_to_customer(self):
        pass
    
    @abstractmethod
    def modify_invoice_email(self, email: str):
        pass
    
    @abstractmethod
    def get_invoices(self):
        pass