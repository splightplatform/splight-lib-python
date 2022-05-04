from django.db import models
from .namespace import NamespaceAwareModel


class Notification(NamespaceAwareModel):
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=100, null=True, blank=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True, blank=True)
