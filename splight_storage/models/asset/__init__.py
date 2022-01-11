from django.db import models
from splight_storage.models.asset.attribute import Attribute
from splight_storage.models.asset.base_asset import BaseAsset
from splight_storage.models.mapping import ValueMapping, ReferenceMapping, ServerMapping, ClientMapping
from typing import Any


class Asset(BaseAsset):
    @staticmethod
    def read(asset: BaseAsset, name: str) -> Any:
        # TODO https://splight.atlassian.net/browse/FAC-236 ClientMapping read from datalake
        try:
            attribute = Attribute.objects.get(name=name)
        except Attribute.DoesNotExist:
            return getattr(asset, name)
        # ReferenceMapping recursive read
        try:
            mapping = ReferenceMapping.objects.get(asset=asset, attribute=attribute)
            return Asset.read(asset=mapping.ref_asset, name=mapping.ref_attribute.name)
        except ReferenceMapping.DoesNotExist:
            pass
        # ValueMapping read
        try:
            return ValueMapping.objects.get(asset=asset, attribute=attribute).value
        except ValueMapping.DoesNotExist:
            pass
        return getattr(asset, name)

    def get(self, name: str) -> Any:
        return Asset.read(asset=self, name=name)

    @staticmethod
    def write(asset, name: str, value: Any) -> None:
        # TODO https://splight.atlassian.net/browse/FAC-236 ClientMapping write from datalake
        try:
            attribute = Attribute.objects.get(name=name)
        except Attribute.DoesNotExist:
            raise AttributeError(f"Attribute '{name}' does not exist")

        # ReferenceMapping recursive write
        try:
            mapping = ReferenceMapping.objects.get(asset=asset, attribute=attribute)
            return Asset.write(asset=mapping.ref_asset, name=mapping.ref_attribute.name, value=value)
        except ReferenceMapping.DoesNotExist:
            pass
        # ValueMapping write
        try:
            mapping = ValueMapping.objects.get(asset=asset, attribute=attribute)
            mapping.value = str(value)
            mapping.save()
            return
        except ValueMapping.DoesNotExist:
            pass

        raise AttributeError(f"Object '{asset}' has not attribute '{name}'")

    def set(self, name: str, value: Any) -> None:
        return Asset.write(asset=self, name=name, value=value)


class Bus(Asset):
    base_voltage = models.FloatField(default=0)
