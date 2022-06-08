from django.db import models
from .namespace import NamespaceAwareModel

class BillingEventType(models.TextChoices):
    START = "start"
    STOP = "stop"

IMPACT_CHOICES = list(zip(range(1,6), range(1,6)))

class BillingEvent(NamespaceAwareModel):
    component_id = models.CharField()
    type = models.CharField(max_length=10, choices=BillingEventType.choices)
    impact = models.IntegerField(max_length=10, choices=IMPACT_CHOICES, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)