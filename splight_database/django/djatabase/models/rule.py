from django.db import models
from .namespace import NamespaceAwareModel


class RuleVariable(NamespaceAwareModel):
    collection = models.CharField(max_length=50)
    filters = models.JSONField(null=True, blank=True)
    key = models.CharField(max_length=50)
    type = models.CharField(max_length=20)


class Rule(NamespaceAwareModel):
    variables = models.ManyToManyField(RuleVariable, blank=True)
    statement = models.CharField(max_length=300)
