from django.db import models
from django.db.models.fields import Field
from model_utils.managers import InheritanceManager
from splight_storage.models.tenant import TenantAwareModel
from splight_storage.models.asset import Asset
from splight_storage.models.connector import Connector


class InvalidFieldException(Exception):
    def __init__(self, conflicts, *args, **kwargs) -> None:
        self.conflicts = conflicts
        super().__init__(*args, **kwargs)


class Mapping(TenantAwareModel):
    path = models.CharField(max_length=300)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    objects = InheritanceManager()

    def save(self, *args, **kwargs):
        try:
            # checking if field is valid
            obj = Asset.objects.get_subclass(id=self.asset.id)
            if self.field not in [f.name for f in obj.__class__._meta.fields]:
                raise InvalidFieldException(self.field)
        except AttributeError:
            pass
        super(Mapping, self).save(*args, **kwargs)


# field and asset are in ClientMapping because 'unique_together' forces them to be local fields
class ClientMapping(Mapping):
    field = models.CharField(max_length=20)
    asset = models.ForeignKey(Asset, related_name="client_mappings", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("field", "asset",)


class ServerMapping(Mapping):
    field = models.CharField(max_length=20)
    asset = models.ForeignKey(Asset, related_name="server_mappings", on_delete=models.CASCADE)
