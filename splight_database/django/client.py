from pydantic import BaseModel
from typing import List, Type
from splight_models import *
from splight_database.abstract import AbstractDatabaseClient
from .djatabase.models import (
    Network as DBNetwork,
    ClientMapping as DBClientMapping,
    ServerMapping as DBServerMapping,
    ValueMapping as DBValueMapping,
    ReferenceMapping as DBReferenceMapping,
    ClientConnector as DBClientConnector,
    ServerConnector as DBServerConnector,
    Asset as DBAsset,
    Attribute as DBAttribute,
    Trigger as DBTrigger,
    TriggerGroup as DBTriggerGroup,
    Tag as DBTag,
    Namespace as DBNamespace,
)
from client import validate_instance_type, validate_resource_type


CLASSMAP = {
    Network: DBNetwork,
    ClientMapping: DBClientMapping,
    ServerMapping: DBServerMapping,
    ValueMapping: DBValueMapping,
    ReferenceMapping: DBReferenceMapping,
    ClientConnector: DBClientConnector,
    ServerConnector: DBServerConnector,
    Asset: DBAsset,
    Attribute: DBAttribute,
    Trigger: DBTrigger,
    TriggerGroup: DBTriggerGroup,
    Tag: DBTag,
}


class DjangoClient(AbstractDatabaseClient):
    valid_classes = list(CLASSMAP.keys())

    def __init__(self, *args, **kwargs) -> None:
        super(DjangoClient, self).__init__(*args, **kwargs)
        self.namespace, _ = DBNamespace.objects.get_or_create(id=self.namespace)

    @validate_instance_type
    def save(self, instance: BaseModel) -> BaseModel:
        default = instance.dict()
        default["namespace"] = self.namespace
        object, _ = CLASSMAP.get(type(instance)).objects.update_or_create(id=instance.id, defaults=default)
        instance.id = str(object.id)
        return instance

    @validate_resource_type
    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        """
        Valid filtering options fields or fields with __in
        """
        queryset = CLASSMAP[resource_type].objects.filter(namespace=self.namespace)
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        if "id" in kwargs:
            kwargs["id"] = int(kwargs["id"])
        if "id__in" in kwargs:
            kwargs["id__in"] = [int(x) for x in kwargs["id__in"]]
        queryset = queryset.filter(**kwargs)

        result = [resource_type(**i.__dict__) for i in queryset]
        if first:
            return result[0] if result else None

        return result

    @validate_resource_type
    def delete(self, resource_type: Type, id: str) -> None:
        CLASSMAP[resource_type].objects.filter(namespace=self.namespace, id=id).delete()
