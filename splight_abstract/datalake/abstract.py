from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List, Dict, Union, Callable
from datetime import datetime, timezone, timedelta
from splight_models import Variable, VariableDataFrame, DatalakeModel
from splight_abstract.client import AbstractClient, QuerySet
from functools import wraps


class AbstractDatalakeClient(AbstractClient):

    valid_filters = ["in", "contains", "gte", "lte"]

    def validate_resource_type(func: Callable) -> Callable:
        @wraps(func)
        def inner(self, resource_type, *args, **kwargs):
            if not issubclass(resource_type, DatalakeModel):
                raise NotImplementedError(f"Not a valid resource_type: {resource_type.__name__}")
            return func(self, resource_type, *args, **kwargs)
        return inner

    @abstractmethod
    def save(self, resource_type: Type, instances: List[BaseModel], collection: str = "default") -> List[BaseModel]:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    def raw_get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, get_func="_raw_get", count_func="raw_count", *args, **kwargs)

    @abstractmethod
    def _get(self,
             resource_type: Type,
             collection: str = 'default',
             limit_: int = 50,
             skip_: int = 0,
             sort: Union[List, str] = ['timestamp__desc'],
             group_id: Union[List, str] = [],
             group_fields: Union[List, str] = [],
             tzinfo: timezone = timezone(timedelta()),
             **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def _raw_get(self,
                 collection: str = 'default',
                 limit_: int = 50,
                 skip_: int = 0,
                 sort: Union[List, str] = ['timestamp__desc'],
                 group_id: Union[List, str] = [],
                 group_fields: Union[List, str] = [],
                 tzinfo: timezone = timezone(timedelta()),
                 **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def count(self,
              resource_type: int,
              collection: str = "default",
              group_id: Union[List, str] = [],
              group_fields: Union[List, str] = [],
              **kwargs) -> int:
        pass

    @abstractmethod
    def raw_count(self,
                  collection: str = "default",
                  group_id: Union[List, str] = [],
                  group_fields: Union[List, str] = [],
                  **kwargs) -> int:
        pass

    @abstractmethod
    def get_dataframe(self, resource_type: Type, freq="H", collection: str = "default") -> VariableDataFrame:
        pass

    @abstractmethod
    def save_dataframe(self, dataframe: VariableDataFrame, collection: str = "default") -> None:
        pass

    @abstractmethod
    def list_collection_names(self) -> List[str]:
        pass

    @abstractmethod
    def get_unique_keys(self, collection: str) -> List[str]:
        pass

    @abstractmethod
    def get_values_for_key(self, collection: str, key: str) -> List[str]:
        pass

    # Subject to incompatibility by implementation
    @abstractmethod
    def raw_aggregate(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
        pass

    def _validated_kwargs(self, resource_type: Type, **kwargs):
        valid_fields: List[str] = list(resource_type.__fields__.keys())

        valid_filter: Dict[str, str] = {
            key: value for key, value in kwargs.items()
            if key in valid_fields or
            any(f"{valid_field}__" in key for valid_field in valid_fields)
        }

        return valid_filter
