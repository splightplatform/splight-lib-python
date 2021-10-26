from django.db import models
from splight_storage.models.tenant import TenantAwareModel


class Tag(TenantAwareModel):
    type = models.CharField(max_length=100)
    value = models.CharField(max_length=100, blank=True)
