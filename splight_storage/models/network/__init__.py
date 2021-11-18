from django.db import models
from model_utils.managers import InheritanceManager
from splight_storage.models.tenant import TenantAwareModel


class Network(TenantAwareModel):
    id = models.BigAutoField(primary_key=True)
    objects = InheritanceManager()

    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'splight_storage'
