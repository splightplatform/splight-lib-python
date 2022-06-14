from django.db import models
from splight_database.django.djatabase.models.asset import Asset, Attribute
from .namespace import NamespaceAwareModel
from .constants import SEVERITIES, OPERATORS, INFO, EQUAL


class MappingRule(NamespaceAwareModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='smappings', null=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='smappings', null=True)
    value = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    message = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITIES, default=INFO)
    operator = models.CharField(max_length=20, choices=OPERATORS, default=EQUAL)
