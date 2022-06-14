from django.db import models
from splight_database.django.djatabase.models.asset import Asset, Attribute
from .namespace import NamespaceAwareModel
from .constants import (
    SYSTEM, LOW, MEDIUM, HIGH, CRITICAL, GREATER_THAN, GREATER_THAN_OR_EQUAL,
    LOWER_THAN, LOWER_THAN_OR_EQUAL, INFO, EQUAL)


OPERATORS = (
    (GREATER_THAN, 'Greater than'),
    (GREATER_THAN_OR_EQUAL, 'Greater than or equal'),
    (LOWER_THAN, 'Lower_than'),
    (LOWER_THAN_OR_EQUAL, 'Lower than or equal'),
    (EQUAL, 'Equal'),
)

SEVERITIES = (
    (SYSTEM, 'system'),
    (INFO, 'info'),
    (LOW, 'low'),
    (MEDIUM, 'medium'),
    (HIGH, 'high'),
    (CRITICAL, 'critical'),
)


class MappingRule(NamespaceAwareModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='smappings', null=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='smappings', null=True)
    value = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    message = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITIES, default=INFO)
    operator = models.CharField(max_length=20, choices=OPERATORS, default=EQUAL)
