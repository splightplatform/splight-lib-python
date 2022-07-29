from django.db import models
from model_utils.managers import InheritanceManager
from .exception import CyclicReference, InvalidReference
from ..connector import Connector
from ..namespace import NamespaceAwareModel
from ..asset import Asset, Attribute
from django.db.models import Q
from django.db.utils import IntegrityError


class Mapping(NamespaceAwareModel):
    objects = InheritanceManager()
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)


class ValueMapping(Mapping):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="value_mappings")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="value_mappings")
    value = models.CharField(max_length=40)

    def save(self, *args, **kwargs):
        validate_unique_mapping(self, *args, **kwargs)
        super(ValueMapping, self).save(*args, **kwargs)


class ReferenceMapping(Mapping):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="reference_mappings")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="reference_mappings")
    ref_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="references")
    ref_attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="references")

    def save(self, *args, **kwargs):        # Prevent to create cyclic
        if ReferenceMapping.objects.filter(
            asset=self.ref_asset,
            attribute=self.ref_attribute,
            ref_asset=self.asset,
            ref_attribute=self.attribute,
        ).exists():
            raise CyclicReference
        validate_unique_mapping(self, *args, **kwargs)
        super(ReferenceMapping, self).save(*args, **kwargs)


class ClientMapping(Mapping):
    asset = models.ForeignKey(Asset, related_name="client_mappings", on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="client_mappings", null=True)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name='cmappings', null=True)
    path = models.CharField(max_length=300, null=True)
    period = models.IntegerField(default=5000)

    def save(self, *args, **kwargs):
        validate_unique_mapping(self, *args, **kwargs)
        super(ClientMapping, self).save(*args, **kwargs)


class ServerMapping(Mapping):
    asset = models.ForeignKey(Asset, related_name="server_mappings", on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="server_mappings", null=True)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name='smappings', null=True)
    path = models.CharField(max_length=300, null=True)


def validate_unique_mapping(self, *args, **kwargs):
    mapping_types = [ClientMapping, ValueMapping, ReferenceMapping]
    mappings = []
    for mapping_type in mapping_types:
        if self.__class__ == mapping_type:
            mappings.append(mapping_type.objects.filter(~Q(id=self.id), asset=self.asset, attribute=self.attribute, deleted=False).exists())
        else:
            mappings.append(mapping_type.objects.filter(asset=self.asset, attribute=self.attribute, deleted=False).exists())
    if any(mappings):
        raise IntegrityError("A mapping already exists for this asset and attribute")


__all__ = ["Mapping",
           "ClientMapping",
           "ServerMapping",
           "ReferenceMapping",
           "ValueMapping",
           "CyclicReference",
           "InvalidReference"]
