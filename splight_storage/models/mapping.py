from django.db import models
from django.db.models.fields import Field
from splight_storage.models.tenant import TenantAwareModel
from splight_storage.models.asset import Asset
from splight_storage.models.connector import Connector


class FieldMapping(TenantAwareModel):
    path = models.CharField(max_length=300)
    field = models.CharField(max_length=20)

    class Meta:
        abstract = True


class ClientMapping(FieldMapping):
    connector = models.ForeignKey(Connector, related_name="client_mappings", on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, related_name="client_mapping", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("field", "asset",)


class ServerMapping(FieldMapping):
    connector = models.ForeignKey(Connector, related_name="server_mappings", on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, related_name="server_mappings", on_delete=models.CASCADE)
