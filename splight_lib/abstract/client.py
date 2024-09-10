from abc import ABC, ABCMeta
from collections import UserList


class empty:
    pass


class SingletonMeta(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class AbstractClient(ABC, metaclass=SingletonMeta):
    pass


class AbstractRemoteClient(AbstractClient):
    def _parse_params(self, **kwargs):
        params = {}
        for key, value in kwargs.items():
            if value is None:
                continue
            params[key] = value
            if isinstance(value, list):
                params[key] = ",".join(value)
        return params


# TODO: Remove this class
class QuerySet(UserList):
    def __init__(
        self,
        client: AbstractClient,
        *args,
        get_func: str = "_get",
        count_func: str = "count",
        **kwargs,
    ):
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
        if kwargs.get("first", False):
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
            # skip_ = self._kwargs.get("skip_", 0) + i.start

            limit_ = i.stop - i.start
            if "limit_" in self._kwargs:
                old_limit_ = self._kwargs["limit_"]
                limit_ = min(limit_, old_limit_)

            kwargs = {**self._kwargs}
            # kwargs["skip_"] = skip_
            # kwargs["limit_"] = limit_
            kwargs.pop("get_func", None)
            kwargs.pop("count_func", None)
            return QuerySet(
                self._client,
                get_func=self._client_func,
                count_func=self._count_func,
                *self._args,
                **kwargs,
            )

        return self.data[i]

    def __len__(self):
        if self._cached_results is not empty:
            return len(self._cached_results)

        if hasattr(self._client, self._count_func):
            return getattr(self._client, self._count_func)(
                *self._args, **self._kwargs
            )

        return len(self.data)

    def first(self):
        result = self[:1]
        return result[0] if result else None

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
