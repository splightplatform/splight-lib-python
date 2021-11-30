from django.db import models
from django.db.models.fields import Field
from model_utils.managers import InheritanceManager
from splight_storage.models.tenant import TenantAwareModel
from splight_storage.models.asset import Asset
from splight_storage.models.connector import Connector


class Mapping(TenantAwareModel):
    path = models.CharField(max_length=300)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    objects = InheritanceManager()


# field and asset are in ClientMapping beacuse 'unique_together' forces them to be local fields
class ClientMapping(Mapping):
    field = models.CharField(max_length=20)
    asset = models.ForeignKey(Asset, related_name="client_mappings", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("field", "asset",)


class ServerMapping(Mapping):
    field = models.CharField(max_length=20)
    asset = models.ForeignKey(Asset, related_name="server_mappings", on_delete=models.CASCADE)
