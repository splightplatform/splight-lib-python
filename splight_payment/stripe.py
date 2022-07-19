from .abstract import AbstractPaymentClient
from .settings import *
import stripe

class StripeClient(AbstractPaymentClient):

    def __init__(self, billing_id: str, *args, **kwargs) -> None:
        super(StripeClient, self).__init__(*args, **kwargs)
        stripe.api_key = STRIPE_APIKEY
        self.customer_id = billing_id

    @staticmethod
    def create_customer(self, name: str, city: str, country: str, postal_code: str, email: str):
        response = stripe.Customer.create(
            name=name, 
            address={'city': city, 'country': country, 'postal_code': postal_code},
            email=email
        )
        return response['id']

    def add_item(self, description: str, price: float):
        ghost_product = stripe.Price.create(unit_amount=int(price*100), currency='usd', product_data={'name': description})
        ghost_product_id = ghost_product['id']
        invoice_item = stripe.InvoiceItem.create(customer=self.customer_id, price= ghost_product_id)

    def close(self):
        invoice = stripe.Invoice.create(customer=self.customer_id, collection_method='send_invoice', days_until_due=7)
        stripe.Invoice.finalize_invoice(invoice['id'])
    
    def get_invoices(self):
        invoice_list = stripe.Invoice.list(customer=self.customer_id, limit=100)['data']
        response = []
        for invoice in invoice_list:
            filtered_invoice = {
                "id" : invoice["id"],
                "total" : invoice["total"],
                "status" : invoice["status"],
                "pdf" : invoice["invoice_pdf"]
            }
            response.append(filtered_invoice)
        return response

        
    def add_card_to_customer(self):
        # not implementing right now
        pass
    

    def modify_invoice_email(self, email: str):
        stripe.Customer.modify(
            customer=self.customer_id,
            email=email
        )