
from django.db import models
from .namespace import NamespaceAwareModel

class BillingSettings(NamespaceAwareModel):
    timestamp = models.DateTimeField()
    pricing = models.JSONField() #Pricing model
    discounts = models.JSONField() # List of discounts
    computing_time_measurement_per_hour = models.BooleanField()