from django.db import models
from .namespace import NamespaceAwareModel

class Rule(NamespaceAwareModel):
    variables = models.JSONField(null=True, blank=True)
    statement = models.CharField(max_length=300)
