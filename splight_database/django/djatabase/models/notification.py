from django.db import models
from .namespace import NamespaceAwareModel


SYSTEM = 'system'
INFO = 'info'
LOW = 'low'
MEDIUM = 'medium'
HIGH = 'high'
CRITICAL = 'critical'

GREATER_THAN = 'gt'
GREATER_THAN_OR_EQUAL = 'ge'
LOWER_THAN = 'lt'
LOWER_THAN_OR_EQUAL = 'le'
EQUAL = 'eq'

SEVERITIES = (
    (SYSTEM, 'system'),
    (INFO, 'info'),
    (LOW, 'low'),
    (MEDIUM, 'medium'),
    (HIGH, 'high'),
    (CRITICAL, 'critical'),
)

SOURCE_TYPE = (
    ('Algorithm', 'Algorithm'),
    ('Network', 'Network'),
    ('Connector', 'Connector'),
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
