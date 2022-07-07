from unittest import TestCase


class TestDatalake(TestCase):
    def test_import_payment(self):
        from splight_lib.payment import PaymentClient