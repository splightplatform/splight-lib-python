from django.db import models
from django.utils.translation import gettext_lazy as _
from .asset import Asset
from .namespace import NamespaceAwareModel


class Algorithm(NamespaceAwareModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    version = models.CharField(max_length=100, null=True, blank=True)
    parameters = models.JSONField()
    readme_url = models.URLField(max_length=200, null=True, blank=True)
