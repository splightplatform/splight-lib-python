from django.db import models
from model_utils.managers import InheritanceManager
from splight_storage.models.tenant import TenantAwareModel


class Network(TenantAwareModel):
    id = models.BigAutoField(primary_key=True)
    objects = InheritanceManager()

    type = models.CharField(max_length=100, default='')
    auth_type = models.CharField(max_length=100, default='')

    class Meta:
        app_label = 'splight_storage'
