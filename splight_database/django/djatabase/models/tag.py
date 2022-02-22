from django.db import models
from .namespace import NamespaceAwareModel


class Tag(NamespaceAwareModel):
    type = models.CharField(max_length=100)
    value = models.CharField(max_length=100, blank=True)
