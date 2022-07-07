from client import AbstractClient
from abc import abstractmethod

class AbstractPaymentClient(AbstractClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @abstractmethod
    def create_customer(self, name: str, city: str, country: str, postal_code: str, email: str):
        pass

    @abstractmethod
    def add_item(self, customer_id:str, description: str, price: float):
        pass
    
    @abstractmethod
    def close(self, customer_id: str):
        pass
    
    @abstractmethod 
    def add_card_to_customer(self, customer_id: str):
        pass
    
    @abstractmethod
    def modify_invoice_email(self, customer_id: str, email: str):
        pass