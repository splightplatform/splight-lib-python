from django.db import models
from .namespace import NamespaceAwareModel


class Tag(NamespaceAwareModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
