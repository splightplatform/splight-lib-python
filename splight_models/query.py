from re import S
from attr import has
from client.abstract import AbstractClient
from django.db.models.query import QuerySet
from collections import UserList


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
