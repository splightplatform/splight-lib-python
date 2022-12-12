from collections import UserList
from pydantic import BaseModel
from typing import List, Type, Callable
from functools import wraps
from abc import ABC
from splight_lib import logging
from .filter import FilterMixin
from .hooks import HooksMixin


logger = logging.getLogger()


class empty:
    pass


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


class AbstractClient(ABC, HooksMixin, FilterMixin):
    valid_classes: List[Type] = []

    def __init__(self, namespace: str = "default", *args, **kwargs):
        self.namespace = namespace.lower().replace("_", "")

    def _validated_kwargs(self, resource_type: Type, **kwargs):
        '''
        Validate the given kwargs.
        '''
        class_fields = list(resource_type.__fields__.keys())
        return super()._validated_kwargs(class_fields, **kwargs)


class QuerySet(UserList):
    def __init__(self,
                 client: AbstractClient,
                 *args,
                 get_func: str = '_get',
                 count_func: str = 'count',
                 **kwargs):
        super().__init__()
        self._client = client
        self._client_func = get_func
        self._count_func = count_func
        self._args = args
        self._kwargs = kwargs
        self._cached_results = empty

    def __new__(cls, *args, **kwargs):
        obj = super(QuerySet, cls).__new__(cls)
        obj.__init__(*args, **kwargs)
        if kwargs.get('first', False):
            return obj.data
        return obj

    def filter(self, **kwargs) -> "QuerySet":
        kwargs = {**self._kwargs, **kwargs}
        return QuerySet(self._client, *self._args, **kwargs)

    def __repr__(self):
        data = [repr(obj) for obj in self[0:4]]
        extra = ", ..." if len(data) > 3 else ""
        return f"QuerySet([{', '.join(data[:3])}{extra}])"

    def __getitem__(self, i):
        if self._cached_results is not empty:
            return self._cached_results[i]

        if isinstance(i, slice):
            skip_ = self._kwargs.get("skip_", 0) + i.start

            limit_ = i.stop - i.start
            if "limit_" in self._kwargs:
                old_limit_ = self._kwargs["limit_"]
                limit_ = min(limit_, old_limit_)

            kwargs = {
                **self._kwargs
            }
            kwargs["skip_"] = skip_
            kwargs["limit_"] = limit_
            kwargs.pop("get_func", None)
            kwargs.pop("count_func", None)
            return QuerySet(self._client, get_func=self._client_func, count_func=self._count_func, *self._args, **kwargs)

        return self.data[i]

    def __len__(self):
        if self._cached_results is not empty:
            return len(self._cached_results)

        if hasattr(self._client, self._count_func):
            return getattr(self._client, self._count_func)(*self._args, **self._kwargs)

        return len(self.data)

    def count(self):
        return len(self)

    @property
    def data(self):
        if self._cached_results is empty:
            client_func = getattr(self._client, self._client_func)
            self._cached_results = client_func(*self._args, **self._kwargs)
        return self._cached_results

    @data.setter
    def data(self, value):
        self._cached_results = value
