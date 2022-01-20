from django.db import models
from typing import Any

from splight_lib import logging
from splight_lib.communication import Message, Variable, ExternalCommunicationClient
from splight_lib.datalake import DatalakeClient
from splight_storage.models.asset.attribute import Attribute
from splight_storage.models.asset.base_asset import BaseAsset
from splight_storage.models.mapping import ValueMapping, ReferenceMapping, ClientMapping


logger = logging.getLogger()


class Asset(BaseAsset):

    @classmethod
    def read(cls, client: DatalakeClient, asset: BaseAsset, name: str) -> Any:
        # Find atributes
        try:
            attribute = Attribute.objects.get(name=name, tenant=asset.tenant)
        except Attribute.DoesNotExist:
            return getattr(asset, name)

        # Datalake read
        try:
            variable: Variable = Variable(asset_id=asset.id, field=name, args=dict())
            variable = client.fetch_updates([variable])
            return variable[0].args["value"]
        except Exception as e:
            logger.debug(str(e))

        # ReferenceMapping recursive read
        try:
            mapping = ReferenceMapping.objects.get(asset=asset, attribute=attribute)
            return cls.read(client=client, asset=mapping.ref_asset, name=mapping.ref_attribute.name)
        except ReferenceMapping.DoesNotExist as e:
            logger.debug(str(e))

        # ValueMapping read
        try:
            return ValueMapping.objects.get(asset=asset, attribute=attribute).value
        except ValueMapping.DoesNotExist as e:
            logger.debug(str(e))

        return getattr(asset, name)

    @classmethod
    def write(cls, client: ExternalCommunicationClient, asset: BaseAsset, name: str, value: Any) -> None:
        # Find atributes
        try:
            attribute = Attribute.objects.get(name=name, tenant=asset.tenant)
        except Attribute.DoesNotExist:
            raise AttributeError(f"Attribute '{name}' does not exist")

        # ExternalQueue write
        if ClientMapping.objects.filter(asset=asset, attribute=attribute).exists():
            variable: Variable = Variable(asset_id=asset.id, field=name, args=dict(value=value))
            msg: Message = Message(action="write", variables=[variable])
            client.send(msg.dict())
            return

        # ReferenceMapping recursive write
        try:
            mapping = ReferenceMapping.objects.get(asset=asset, attribute=attribute)
            return cls.write(client=client, asset=mapping.ref_asset, name=mapping.ref_attribute.name, value=value)
        except ReferenceMapping.DoesNotExist as e:
            logger.debug(str(e))


        # ValueMapping write
        try:
            mapping = ValueMapping.objects.get(asset=asset, attribute=attribute)
            mapping.value = value
            mapping.save()
            return
        except ValueMapping.DoesNotExist as e:
            logger.debug(str(e))

        raise AttributeError(f"Object '{asset}' has not attribute '{name}'")

    def get(self, name: str, default=None) -> Any:
        tenant_name = "default"
        if self.tenant is not None:
            tenant_name = self.tenant.org_id
        dl_client = DatalakeClient(tenant_name)
        try:
            return self.read(client=dl_client, asset=self, name=name)
        except AttributeError as e:
            if default:
                return default
            raise e

    def set(self, name: str, value: Any) -> None:
        tenant_name = "default"
        if self.tenant is not None:
            tenant_name = self.tenant.org_id
        q_client = ExternalCommunicationClient(tenant_name)
        return self.write(client=q_client, asset=self, name=name, value=value)


class Bus(Asset):
    base_voltage = models.FloatField(default=0)
