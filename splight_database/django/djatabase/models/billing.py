
from django.db import models
from .namespace import NamespaceAwareModel

class BillingSettings(NamespaceAwareModel):
    timestamp = models.DateTimeField()
    pricing = models.JSONField() #Pricing model
    discounts = models.JSONField() # List of discounts
    computing_time_measurement_per_hour = models.BooleanField()

class MonthBilling(NamespaceAwareModel):
    month = models.DateTimeField()
    discount_detail = models.CharField(max_length=255)
    discount_value = models.DecimalField(max_digits=1000, decimal_places=2)
    total_price_without_discount = models.DecimalField(max_digits=1000, decimal_places=2)
    total_price = models.DecimalField(max_digits=1000, decimal_places=2)
    paid = models.BooleanField()

class Billing(NamespaceAwareModel):
    month_billing = models.ForeignKey(MonthBilling, on_delete=models.CASCADE, related_name='billings')
    description = models.CharField(max_length=1000)
    items_type = models.CharField(max_length=255)
    detailed_pricing = models.JSONField()
    total_price = models.FloatField()

class BillingItem(NamespaceAwareModel):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=1000)
    total_price = models.FloatField()

class DeploymentBillingItem(BillingItem):
    computing_price = models.FloatField()
    storage_price = models.FloatField()