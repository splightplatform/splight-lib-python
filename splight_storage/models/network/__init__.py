from typing import Protocol
from django.db import models
from django.db.models.fields import files
from model_utils.managers import InheritanceManager
from splight_storage.models.tenant import TenantAwareModel


class Network(TenantAwareModel):
    id = models.BigAutoField(primary_key=True)
    objects = InheritanceManager()

    class Meta:
        app_label = 'splight_storage'
