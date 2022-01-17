from django.db import models
from splight_lib.communication import Message, Variable, ExternalCommunicationClient
from splight_lib.datalake import DatalakeClient
from splight_storage.models.asset.attribute import Attribute
from splight_storage.models.asset.base_asset import BaseAsset
from splight_storage.models.mapping import ValueMapping, ReferenceMapping, ServerMapping, ClientMapping

from typing import Any


EXTERNAL_QUEUE = ExternalCommunicationClient()


class Asset(BaseAsset):
    def read(self, asset: BaseAsset, name: str) -> Any:
        # Find atributes
        try:
            attribute = Attribute.objects.get(name=name)
        except Attribute.DoesNotExist:
            return getattr(asset, name)

        # Datalake read
        try:
            variable: Variable = Variable(asset_id=asset.id, field=name, args=dict())
            variable = self.dl_client.fetch_updates([variable])
            return variable[0].args["value"]
        except Exception:
            pass

        # ReferenceMapping recursive read
        try:
            mapping = ReferenceMapping.objects.get(asset=asset, attribute=attribute)
            return self.read(asset=mapping.ref_asset, name=mapping.ref_attribute.name)
        except ReferenceMapping.DoesNotExist:
            pass

        # ValueMapping read
        try:
            return ValueMapping.objects.get(asset=asset, attribute=attribute).value
        except ValueMapping.DoesNotExist:
            pass

        return getattr(asset, name)

    def get(self, name: str, *args, **kwargs) -> Any:
        try:
            tenant = self.tenant.org_id
        except AttributeError:
            tenant = "default"

        self.dl_client = DatalakeClient(tenant)
        try:
            return self.read(asset=self, name=name)
        except AttributeError as e:
            if 'default' in kwargs:
                return kwargs['default']
            elif len(args) > 0:
                return args[0]
            else:
                raise e

    @staticmethod
    def write(asset, name: str, value: Any) -> None:
        # Find atributes
        try:
            attribute = Attribute.objects.get(name=name)
        except Attribute.DoesNotExist:
            raise AttributeError(f"Attribute '{name}' does not exist")

        # ExternalQueue write
        if ClientMapping.objects.filter(asset=asset, attribute=attribute).exists():
            variable: Variable = Variable(asset_id=asset.id, field=name, args=dict(value=value))
            msg: Message = Message(action="write", variables=[variable])
            EXTERNAL_QUEUE.send(msg.dict())
            return

        # ReferenceMapping recursive write
        try:
            mapping = ReferenceMapping.objects.get(asset=asset, attribute=attribute)
            return Asset.write(asset=mapping.ref_asset, name=mapping.ref_attribute.name, value=value)
        except ReferenceMapping.DoesNotExist:
            pass

        raise AttributeError(f"Object '{asset}' has not attribute '{name}'")

    def set(self, name: str, value: Any) -> None:
        return Asset.write(asset=self, name=name, value=value)


class Bus(Asset):
    base_voltage = models.FloatField(default=0)
