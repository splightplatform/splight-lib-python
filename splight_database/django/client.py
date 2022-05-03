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
    Connector as DBConnector,
    Asset as DBAsset,
    Attribute as DBAttribute,
    Rule as DBRule,
    Tag as DBTag,
    Namespace as DBNamespace,
    Algorithm as DBAlgorithm,
    Dashboard as DBDashboard,
    Tab as DBTab,
    Filter as DBFilter,
    ChartItem as DBChartItem,
    Chart as DBChart,
    Notification as DBNotification,
)
from client import validate_instance_type, validate_resource_type


CLASSMAP = {
    Network: DBNetwork,
    ClientMapping: DBClientMapping,
    ServerMapping: DBServerMapping,
    ValueMapping: DBValueMapping,
    ReferenceMapping: DBReferenceMapping,
    Connector: DBConnector, 
    Asset: DBAsset,
    Attribute: DBAttribute,
    Rule: DBRule,
    Tag: DBTag,
    Namespace: DBNamespace,
    Algorithm: DBAlgorithm,
    Dashboard: DBDashboard,
    Tab: DBTab,
    Filter: DBFilter,
    ChartItem: DBChartItem,
    Chart: DBChart,
    Notification: DBNotification,
}


class DjangoClient(AbstractDatabaseClient):
    valid_classes = list(CLASSMAP.keys())

    def __init__(self, *args, **kwargs) -> None:
        super(DjangoClient, self).__init__(*args, **kwargs)
        self.namespace, _ = DBNamespace.objects.get_or_create(id=self.namespace)

    @validate_instance_type
    def save(self, instance: BaseModel) -> BaseModel:
        data = instance.dict()
        obj_class = CLASSMAP.get(type(instance))
        for m2m_field in obj_class._meta.local_many_to_many:
            data.pop(m2m_field.name, [])
        if hasattr(obj_class, "namespace"):
            data["namespace"] = self.namespace
        object, _ = obj_class.objects.update_or_create(id=instance.id, defaults=data)
        for m2m_field in obj_class._meta.local_many_to_many:
            getattr(object, m2m_field.name).set(instance.dict().get(m2m_field.name, []))
        instance.id = str(object.id)
        return instance

    @validate_resource_type
    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        """
        Valid filtering options fields or fields with __in
        """
        obj_class = CLASSMAP[resource_type]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        if hasattr(obj_class, "namespace"):
            kwargs["namespace"] = self.namespace
        queryset = obj_class.objects.filter(**kwargs).distinct()
        result = [resource_type(**i.to_dict()) for i in queryset]

        if first:
            return result[0] if result else None

        return result

    @validate_resource_type
    def delete(self, resource_type: Type, id: str) -> None:
        obj_class = CLASSMAP[resource_type]
        filters = {"id": id}
        if hasattr(obj_class, "namespace"):
            filters["namespace"] = self.namespace
        obj_class.objects.filter(**filters).delete()
