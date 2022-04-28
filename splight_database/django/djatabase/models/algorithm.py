from django.db import models
from django.utils.translation import gettext_lazy as _
from .namespace import NamespaceAwareModel


class Algorithm(NamespaceAwareModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    version = models.CharField(max_length=100, null=True, blank=True)
    parameters = models.JSONField()