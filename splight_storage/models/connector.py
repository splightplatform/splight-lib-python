from django.db import models
from splight_storage.models.tenant import TenantAwareModel


class Connector(TenantAwareModel):
    network = models.IntegerField()
    ip = models.GenericIPAddressField()
