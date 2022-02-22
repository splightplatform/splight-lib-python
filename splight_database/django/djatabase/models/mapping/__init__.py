from django.db import models
from model_utils.managers import InheritanceManager

from .exception import CyclicReference, InvalidReference
from ..connector import ClientConnector, ServerConnector
from ..namespace import NamespaceAwareModel
from ..asset import Asset, Attribute


class Mapping(NamespaceAwareModel):
    objects = InheritanceManager()


class ValueMapping(Mapping):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="value_mappings")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="value_mappings")
    value = models.CharField(max_length=40)

    class Meta:
        unique_together = ("attribute", "asset",)


class ReferenceMapping(Mapping):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="reference_mappings")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="reference_mappings")
    ref_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="references")
    ref_attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="references")
    value = models.CharField(max_length=40)

    class Meta:
        unique_together = ("attribute", "asset",)

    def save(self, *args, **kwargs):
        # Prevent to create cyclic
        if ReferenceMapping.objects.filter(
            asset=self.ref_asset,
            attribute=self.ref_attribute,
            ref_asset=self.asset,
            ref_attribute=self.attribute,
        ).exists():
            raise CyclicReference
        super(ReferenceMapping, self).save(*args, **kwargs)


class ClientMapping(Mapping):
    asset = models.ForeignKey(Asset, related_name="client_mappings", on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="client_mappings", null=True)
    connector = models.ForeignKey(ClientConnector, on_delete=models.CASCADE, related_name='mappings', null=True)
    path = models.CharField(max_length=300, null=True)

    class Meta:
        unique_together = ("attribute", "asset",)


class ServerMapping(Mapping):
    asset = models.ForeignKey(Asset, related_name="server_mappings", on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="server_mappings", null=True)
    connector = models.ForeignKey(ServerConnector, on_delete=models.CASCADE, related_name='mappings', null=True)
    path = models.CharField(max_length=300, null=True)


__all__ = ["Mapping",
           "ClientMapping",
           "ServerMapping",
           "ReferenceMapping",
           "ValueMapping",
           "CyclicReference",
           "InvalidReference"]
