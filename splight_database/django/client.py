from pydantic import BaseModel
from typing import List, Type, TypeGuard
from splight_models import *
from splight_database.abstract import AbstractDatabaseClient
from .djatabase.models import (
    Algorithm as DBAlgorithm,
    Asset as DBAsset,
    Attribute as DBAttribute,
    BillingSettings as DBBillingSettings,
    MonthBilling as DBMonthBilling,
    Billing as DBBilling,
    DeploymentBillingItem as DBDeploymentBillingItem,
    Chart as DBChart,
    ChartItem as DBChartItem,
    Connector as DBConnector,
    ClientMapping as DBClientMapping,
    Dashboard as DBDashboard,
    Edge as DBEdge,
    Filter as DBFilter,
    Graph as DBGraph,
    Namespace as DBNamespace,
    Network as DBNetwork,
    Notification as DBNotification,
    Node as DBNode,
    MappingRule as DBMappingRule,
    ReferenceMapping as DBReferenceMapping,
    ServerMapping as DBServerMapping,
    Tab as DBTab,
    Tag as DBTag,
    ValueMapping as DBValueMapping,
)
from client import validate_instance_type, validate_resource_type
from splight_models.query import QuerySet

CLASSMAP = {
    Algorithm: DBAlgorithm,
    Asset: DBAsset,
    Attribute: DBAttribute,
    BillingSettings: DBBillingSettings,
    MonthBilling: DBMonthBilling,
    Billing: DBBilling,
    DeploymentBillingItem: DBDeploymentBillingItem,
    Chart: DBChart,
    ChartItem: DBChartItem,
    Connector: DBConnector,
    ClientMapping: DBClientMapping,
    Dashboard: DBDashboard,
    Edge: DBEdge,
    Filter: DBFilter,
    Graph: DBGraph,
    Namespace: DBNamespace,
    Network: DBNetwork,
    Notification: DBNotification,
    Node: DBNode,
    MappingRule: DBMappingRule,
    ReferenceMapping: DBReferenceMapping,
    ServerMapping: DBServerMapping,
    Tab: DBTab,
    Tag: DBTag,
    ValueMapping: DBValueMapping,
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
    def _get(self, resource_type: Type,
             first: bool = False,
             limit: int = -1,
             skip_: int = 0,
             **kwargs) -> List[BaseModel]:
        """
        Valid filtering options fields or fields with __in
        """
        obj_class = CLASSMAP[resource_type]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        if hasattr(obj_class, "namespace"):
            kwargs["namespace"] = self.namespace
        queryset = obj_class.objects.filter(**kwargs).distinct()
        if limit != -1:
            queryset = queryset[skip_:skip_ + limit]

        result = [resource_type(**i.to_dict()) for i in queryset]

        if first:
            return result[0] if result else None

        return result

    @validate_resource_type
    def count(self, resource_type: Type, **kwargs):
        obj_class = CLASSMAP[resource_type]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        if hasattr(obj_class, "namespace"):
            kwargs["namespace"] = self.namespace
        queryset = obj_class.objects.filter(**kwargs).distinct()
        return queryset.count()

    @validate_resource_type
    def delete(self, resource_type: Type, id: str) -> None:
        obj_class = CLASSMAP[resource_type]
        filters = {"id": id}
        if hasattr(obj_class, "namespace"):
            filters["namespace"] = self.namespace
        obj_class.objects.filter(**filters).delete()
