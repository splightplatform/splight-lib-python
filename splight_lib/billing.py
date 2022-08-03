import os

from fake_splight_lib.billing import FakeBillingClient
from splight_billing.stripe.stripe import StripeClient


REGISTRY = {
    "fake": FakeBillingClient,
    "stripe": StripeClient,
}

BillingClient = REGISTRY.get(os.environ.get("BILLING", "fake"))
