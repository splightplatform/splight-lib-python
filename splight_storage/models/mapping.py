from django.db import models
from django.db.models.fields import Field
from model_utils.managers import InheritanceManager
from splight_storage.models.tenant import TenantAwareModel
from splight_storage.models.asset import Asset
from splight_storage.models.connector import ClientConnector, Connector, ServerConnector


class InvalidFieldException(Exception):
    pass


class Mapping(TenantAwareModel):
    path = models.CharField(max_length=300)
    objects = InheritanceManager()

    def save(self, *args, **kwargs):
        try:
            # checking if field is valid
            obj = Asset.objects.get_subclass(id=self.asset.id)
            if self.field not in [f.name for f in obj.__class__._meta.fields]:
                raise InvalidFieldException(f"Field {self.field} not present in asset {obj}")
        except AttributeError:
            pass
        super(Mapping, self).save(*args, **kwargs)


class ClientMapping(Mapping):
    field = models.CharField(max_length=20)
    asset = models.ForeignKey(Asset, related_name="client_mappings", on_delete=models.CASCADE)
    connector = models.ForeignKey(ClientConnector, on_delete=models.CASCADE, related_name='mappings', null=True)

    class Meta:
        unique_together = ("field", "asset",)


class ServerMapping(Mapping):
    field = models.CharField(max_length=20)
    asset = models.ForeignKey(Asset, related_name="server_mappings", on_delete=models.CASCADE)
    connector = models.ForeignKey(ServerConnector, on_delete=models.CASCADE, related_name='mappings', null=True)
