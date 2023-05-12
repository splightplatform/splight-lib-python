from abc import abstractmethod
from datetime import timedelta, timezone
from functools import wraps
from typing import Callable, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel
from splight_abstract.client import AbstractClient, QuerySet
from splight_models import DatalakeModel


def validate_datalake_resource_type(func: Callable) -> Callable:
    @wraps(func)
    def inner(self, resource_type, *args, **kwargs):
        if not issubclass(resource_type, DatalakeModel):
            raise NotImplementedError(
                f"Not a valid resource_type: {resource_type.__name__}"
            )
        return func(self, resource_type, *args, **kwargs)

    return inner


def validate_datalake_instance_type(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, instances: List[BaseModel], *args, **kwargs):
        if instances:
            resource_type = instances[0].__class__
            if not all([isinstance(i, resource_type) for i in instances]):
                raise TypeError("All instances must be of the same type")
            if not issubclass(resource_type, DatalakeModel):
                raise TypeError("All instances must be of type DatalakeModel")
        return func(self, instances, *args, **kwargs)

    return wrapper


class AbstractDatalakeClient(AbstractClient):
    def get(self, *args, **kwargs) -> QuerySet:
        kwargs["get_func"] = "_raw_get"
        kwargs["count_func"] = "None"
        return QuerySet(self, *args, **kwargs)

    @abstractmethod
    def save(
        self, collection: str, instances: Union[List[Dict], Dict]
    ) -> List[DatalakeModel]:
        pass

    @abstractmethod
    def delete(self, collection: str, **kwargs) -> None:
        pass

    @abstractmethod
    def get_dataframe(
        self,
        resource_name: str,
        collection: str,
        sort: Union[List, str] = ["timestamp__desc"],
        group_id: Optional[Union[List, str]] = None,
        group_fields: Optional[Union[List, str]] = None,
        tzinfo: timezone = timezone(timedelta()),
        **filters,
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def save_dataframe(self, collection: str, dataframe: pd.DataFrame) -> None:
        pass

    @abstractmethod
    def create_index(self, collection: str, indexes: List[Dict]) -> None:
        pass

    @abstractmethod
    def raw_aggregate(
        self, collection: str, pipeline: List[Dict]
    ) -> List[Dict]:
        pass

    @abstractmethod
    def _raw_get(
        self,
        resource_name: str,
        collection: str,
        limit_: int = 50,
        skip_: int = 0,
        sort: Union[List, str] = ["timestamp__desc"],
        group_id: Optional[Union[List, str]] = None,
        group_fields: Optional[Union[List, str]] = None,
        tzinfo: timezone = timezone(timedelta()),
        **filters,
    ) -> List[Dict]:
        pass
