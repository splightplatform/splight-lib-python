
from django.db import models
from .namespace import NamespaceAwareModel

class BillingSettings(NamespaceAwareModel):
    timestamp = models.DateTimeField()
    pricing = models.JSONField() #Pricing model
    discounts = models.JSONField() # List of discounts
    computing_time_measurement_per_hour = models.BooleanField()

class MonthBilling(NamespaceAwareModel):
    month = models.DateTimeField()
    billings = models.JSONField() # List of billings
    discount = models.JSONField(null=True) # Discount model
    discount_value = models.DecimalField(max_digits=1000, decimal_places=2)
    total_price_without_discount = models.DecimalField(max_digits=1000, decimal_places=2)
    total_price = models.DecimalField(max_digits=1000, decimal_places=2)
    paid = models.BooleanField()
