from collections import UserList
from pydantic import BaseModel
from typing import List, Type, Callable
from functools import wraps
from abc import ABC
from splight_lib import logging
from .pre_hook import PreHookMixin


logger = logging.getLogger()


def validate_resource_type(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, resource_type: Type, *args, **kwargs):
        if resource_type not in self.valid_classes:
            raise NotImplementedError(f"Not a valid resource_type: {resource_type.__name__}")
        return func(self, resource_type, *args, **kwargs)
    return wrapper


def validate_instance_type(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, instance: BaseModel, *args, **kwargs):
        if type(instance) not in self.valid_classes:
            raise NotImplementedError(f"Not a valid instance type: {type(instance).__name__}")
        return func(self, instance, *args, **kwargs)
    return wrapper


class AbstractClient(ABC, PreHookMixin):
    valid_classes: List[Type] = []

    def __init__(self, namespace: str = "default", *args, **kwargs):
        self.namespace = namespace.lower().replace("_", "")

    def _filter(self, queryset: List[BaseModel], **kwargs) -> List[BaseModel]:
        '''
        Filter a queryset by the given kwargs.
        '''
        field_filters = [
            lambda x, field=field, value=value: getattr(x, field) == value for field, value in kwargs.items() if "__" not in field
        ]
        in_filters = [
            lambda x, field=field, values=values: getattr(x, field.replace("__in", "")) in values for field, values in kwargs.items() if field.endswith("__in")
        ]
        contains_filters = [
            lambda x, field=field, value=value: value in getattr(x, field.replace("__contains", "")) for field, value in kwargs.items() if field.endswith("__contains")
        ]

        filters = field_filters + in_filters + contains_filters

        return [obj for obj in queryset if all([f(obj) for f in filters])]

    def _validated_kwargs(self, resource_type: Type, **kwargs):
        '''
        Validate the given kwargs.
        '''
        class_fields = list(resource_type.__fields__.keys())
        valid_kwargs = [
            f"{field}__in" for field in class_fields
        ] + [
            f"{field}__contains" for field in class_fields
        ] + [
            f"{field}__lte" for field in class_fields
        ] + [
            f"{field}__gte" for field in class_fields
        ] + class_fields

        invalid_kwargs = [key for key in kwargs.keys() if key not in valid_kwargs]
        for key in invalid_kwargs:
            kwargs.pop(key)
        return kwargs


class QuerySet(UserList):
    def __init__(self, client: AbstractClient, *args, **kwargs):
        super().__init__()
        self._client = client
        self._args = args
        self._kwargs = kwargs
        self._cached_results = None

    def __new__(cls, *args, **kwargs):
        obj = super(QuerySet, cls).__new__(cls)
        obj.__init__(*args, **kwargs)
        if kwargs.get('first', False):
            return obj.data
        return obj

    def filter(self, **kwargs) -> "QuerySet":
        kwargs = {**self._kwargs, **kwargs}
        return QuerySet(self._client, *self._args, **kwargs)

    def __getitem__(self, i):
        if self._cached_results:
            return self._cached_results[i]

        if isinstance(i, slice):
            kwargs = {
                "skip_": i.start,
                "limit_": i.stop - i.start,
                **self._kwargs
            }
            return QuerySet(self._client, *self._args, **kwargs)
        else:
            return self.data[i]

    def __len__(self):
        if self._cached_results:
            return len(self._cached_results)

        if hasattr(self._client, "count"):
            return self._client.count(*self._args, **self._kwargs)

        return len(self.data)

    def count(self):
        return len(self)

    @property
    def data(self):
        if self._cached_results is None:
            self._cached_results = self._client._get(*self._args, **self._kwargs)
        return self._cached_results

    @data.setter
    def data(self, value):
        self._cached_results = value
