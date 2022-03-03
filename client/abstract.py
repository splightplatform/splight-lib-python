from pydantic import BaseModel
from typing import List, Type, Callable
from functools import wraps
from abc import ABC


def validate_resource_type(func: Callable):
    @wraps(func)
    def wrapper(self, resource_type: Type, *args, **kwargs):
        if resource_type not in self.valid_classes:
            raise NotImplementedError
        return func(self, resource_type, *args, **kwargs)
    return wrapper


def validate_instance_type(func: Callable):
    @wraps(func)
    def wrapper(self, instance: BaseModel, *args, **kwargs):
        if type(instance) not in self.valid_classes:
            raise NotImplementedError
        return func(self, instance, *args, **kwargs)
    return wrapper


class AbstractClient(ABC):
    valid_classes: List[Type] = []

    def __init__(self, namespace: str = "default", *args, **kwargs):
        self.namespace = namespace.lower().replace("_", "")

    def _filter(self, queryset: List[BaseModel], **kwargs) -> List[BaseModel]:
        '''
        Filter a queryset by the given kwargs.
        '''
        field_filters = [
            lambda x, field=field, value=value: getattr(x, field) == value for field, value in kwargs.items() if not field.endswith("__in")
        ]
        in_filters = [
            lambda x, field=field, values=values: getattr(x, field) in values for field, values in kwargs.items() if field.endswith("__in")
        ]
        filters = field_filters + in_filters
        return [obj for obj in queryset if all([f(obj) for f in filters])]

    def _validated_kwargs(self, resource_type: Type, **kwargs):
        '''
        Validate the given kwargs.
        '''
        class_fields = list(resource_type.__fields__.keys())
        valid_kwargs = [
            f"{field}__in" for field in class_fields
        ] + class_fields

        invalid_kwargs = [key for key in kwargs.keys() if key not in valid_kwargs]
        for key in invalid_kwargs:
            kwargs.pop(key)
        return kwargs
