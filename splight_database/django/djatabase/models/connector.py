from django.db import models
from django.utils.translation import gettext_lazy as _
from .namespace import NamespaceAwareModel


class Connector(NamespaceAwareModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    version = models.CharField(max_length=100, null=True, blank=True)
    privacy_policy = models.CharField(max_length=100, null=True, blank=True)
    tenant = models.CharField(max_length=100, null=True, blank=True)
    parameters = models.JSONField(default=dict)
    readme_url = models.URLField(max_length=200, null=True, blank=True)