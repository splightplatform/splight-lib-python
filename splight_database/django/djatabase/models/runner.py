from django.db import models
from .namespace import NamespaceAwareModel


class Runner(NamespaceAwareModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    tag_id = models.CharField(max_length=100, null=True, blank=True)
    version = models.CharField(max_length=100, null=True, blank=True)
    parameters = models.JSONField()