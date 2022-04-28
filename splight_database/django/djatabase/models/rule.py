from django.db import models
from .namespace import NamespaceAwareModel


class Rule(NamespaceAwareModel):
    name = models.CharField(max_length=100, default='Rule')
    description = models.CharField(max_length=100, null=True, blank=True)
    variables = models.JSONField(null=True, blank=True)
    statement = models.CharField(max_length=300)
