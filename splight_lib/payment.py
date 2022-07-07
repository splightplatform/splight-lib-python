from splight_payment import StripeClient
import os

SELECTOR = {
    'fake': StripeClient,
    'stripe': StripeClient,
}

PaymentClient = SELECTOR.get(os.environ.get('PAYMENT', 'fake'))

__all__ = [
    "PaymentClient",
]
