from .abstract import AbstractPaymentClient
from .settings import *
import stripe

class StripeClient(AbstractPaymentClient):

    def __init__(self, *args, **kwargs) -> None:
        super(StripeClient, self).__init__(*args, **kwargs)
        stripe.api_key = STRIPE_APIKEY

    def create_customer(self, name: str, city: str, country: str, postal_code: str, email: str):
        response = stripe.Customer.create(
            name=name, 
            address={'city': city, 'country': country, 'postal_code': postal_code},
            email=email
        )
        return response['id']

    def add_item(self, customer_id: str, description: str, price: float):
        ghost_product = stripe.Price.create(unit_amount=int(price*100), currency='usd', product_data={'name': description})
        ghost_product_id = ghost_product['id']
        invoice_item = stripe.InvoiceItem.create(customer=customer_id, price= ghost_product_id)

    def close(self, customer_id: str):
        invoice = stripe.Invoice.create(customer=customer_id, collection_method='send_invoice', days_until_due=7)
    
    def add_card_to_customer(self, customer_id: str):
        pass
    

    def modify_invoice_email(self, customer_id: str, email: str):
        pass