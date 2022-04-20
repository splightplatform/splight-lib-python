from django.db import models
from .namespace import NamespaceAwareModel


class Rule(NamespaceAwareModel):
    collection = models.CharField(max_length=50)
    filters = models.CharField(max_length=300)


class Trigger(NamespaceAwareModel):
    rule = models.CharField(max_length=300)