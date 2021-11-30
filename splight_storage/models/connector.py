from django.db import models
from splight_storage.models.tenant import TenantAwareModel
from splight_storage.models.network import Network


class Connector(TenantAwareModel):
    network = models.ForeignKey(Network, related_name="connectors", on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
