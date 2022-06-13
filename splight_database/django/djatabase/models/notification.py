from django.db import models
from .namespace import NamespaceAwareModel
from .constants import SEVERITIES, INFO, SOURCE_TYPE


class Notification(NamespaceAwareModel):
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=100, null=True, blank=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITIES, null=False, default=INFO)
    asset_id = models.CharField(null=True, max_length=100)
    attribute_id = models.CharField(null=True, max_length=100)
    rule_id = models.CharField(null=True, max_length=100)
    source_id = models.CharField(null=True, max_length=100)
    source_type = models.CharField(max_length=20, choices=list(zip(SOURCE_TYPE, SOURCE_TYPE)), null=True)
