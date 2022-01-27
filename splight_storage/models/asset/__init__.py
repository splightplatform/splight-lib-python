from re import S
from django.db import models
from django.db.models import Q
from typing import Any, List

from splight_lib import logging
from splight_lib.communication import Message, Variable, ExternalCommunicationClient
from splight_lib.datalake import DatalakeClient
from splight_storage.models.asset.attribute import Attribute
from splight_storage.models.asset.base_asset import BaseAsset
from splight_storage.models.mapping import ValueMapping, ReferenceMapping, ClientMapping
from splight_storage.models.mapping.mappings import ResolvedValueMapping, ResolvedMapping, ResolvedClientMapping

logger = logging.getLogger()


def _resolve_attribute(asset: BaseAsset, attr: Attribute, original_attr: Attribute) -> ResolvedMapping:
    """
    This function resolves an attribute values to be eather a values o client mappings.
    if the attribute has multiple mappings the priority is: client > reference > value.
    """
    client_mapping: ClientMapping = asset.client_mappings.filter(attribute=attr)
    if client_mapping.exists():
        client_mapping = client_mapping.first()
        return ResolvedClientMapping(attr=original_attr.name, ref_attr=attr.name, asset_id=asset.id)

    reference_mapping: ReferenceMapping = asset.reference_mappings.filter(attribute=attr)
    if reference_mapping.exists():
        reference_mapping = reference_mapping.first()
        return _resolve_attribute(reference_mapping.ref_asset, reference_mapping.ref_attribute, original_attr)

    value_mapping: ValueMapping = asset.value_mappings.filter(attribute=attr).first()
    return ResolvedValueMapping(attr=original_attr.name, asset_id=asset.pk, value=value_mapping.value)


class Asset(BaseAsset):
    @property
    def attributes(self):
        return Attribute.objects.filter(Q(client_mappings__asset=self) |
                                        Q(server_mappings__asset=self) |
                                        Q(value_mappings__asset=self) |
                                        Q(reference_mappings__asset=self)).distinct()

    def resolve_attributes(self, Attributes: List[str]) -> List[ResolvedMapping]:
        resolved_attributes: List[ResolvedMapping] = []
        for attr in Attributes:
            original_attr = self.attributes.filter(name=attr)
            if original_attr.exists():
                original_attr = original_attr.first()
                resolved_attributes.append(_resolve_attribute(self, original_attr, original_attr))
        return resolved_attributes

    def read(self, client: DatalakeClient, asset: BaseAsset, name: str) -> Any:
        attribute: Attribute = asset.attributes.filter(name=name)
        if not attribute.exists():
            return getattr(asset, name)

        resolved_mapping = self.resolve_attributes([name])[0]
        if resolved_mapping.type == "client":
            try:
                variable: Variable = Variable(asset_id=resolved_mapping.asset_id,
                                              field=resolved_mapping.ref_attr,
                                              args=dict())
                variable = client.fetch_updates([variable])
                return variable[0].args["value"]
            except Exception as e:
                logger.debug(str(e))
        else:
            return resolved_mapping.value

    def write(self, client: ExternalCommunicationClient, asset: BaseAsset, name: str, value: Any) -> None:
        attribute: Attribute = asset.attributes.filter(name=name)
        if not attribute.exists():
            raise AttributeError(f"Attribute '{name}' does not exist")

        resolved_mapping = self.resolve_attributes([name])[0]
        if resolved_mapping.type == "client":
            variable: Variable = Variable(asset_id=asset.id, field=resolved_mapping.ref_attr, args=dict(value=value))
            msg: Message = Message(action="write", variables=[variable])
            client.send(msg.dict())
        else:
            mapping = ValueMapping.objects.get(asset__pk=resolved_mapping.asset_id,
                                               attribute__name=resolved_mapping.attr)
            mapping.value = value
            mapping.save()

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