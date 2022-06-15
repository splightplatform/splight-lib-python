from django.db import models
from splight_database.django.djatabase.models.asset import Asset, Attribute
from .namespace import NamespaceAwareModel


class MappingRule(NamespaceAwareModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='smappings', null=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='smappings', null=True)
    value = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    message = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
