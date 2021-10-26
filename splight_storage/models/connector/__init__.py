from django.db import models
from model_utils.managers import InheritanceManager
from splight_storage.models.tenant import TenantAwareModel


class ConnectorInterface(TenantAwareModel):
    objects = InheritanceManager()

    class Meta:
        app_label = 'splight_storage'
