from django.db import models
from .namespace import NamespaceAwareModel
from .constants import (SYSTEM, LOW, MEDIUM, HIGH, CRITICAL, INFO, ALGORITHM, NETWORK, CONNECTOR)


SEVERITIES = (
    (SYSTEM, 'system'),
    (INFO, 'info'),
    (LOW, 'low'),
    (MEDIUM, 'medium'),
    (HIGH, 'high'),
    (CRITICAL, 'critical'),
)


SOURCE_TYPE = (
    (ALGORITHM, 'Algorithm'),
    (NETWORK, 'Network'),
    (CONNECTOR, 'Connector'),
)


class Notification(NamespaceAwareModel):
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=100, null=True, blank=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITIES, default=INFO, blank=True, null=True)
    asset_id = models.CharField(null=True, max_length=100)
    attribute_id = models.CharField(null=True, max_length=100)
    rule_id = models.CharField(null=True, max_length=100)
    source_id = models.CharField(null=True, max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE, null=True)
