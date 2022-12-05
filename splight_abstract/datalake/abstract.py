from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List, Dict, Union, Callable
from datetime import timezone, timedelta
from splight_models import DatalakeModel, Query
from splight_abstract.client import AbstractClient, QuerySet
from functools import wraps
import pandas as pd


def validate_resource_type(func: Callable) -> Callable:
    @wraps(func)
    def inner(self, resource_type, *args, **kwargs):
        if not issubclass(resource_type, DatalakeModel):
            raise NotImplementedError(f"Not a valid resource_type: {resource_type.__name__}")
        return func(self, resource_type, *args, **kwargs)
    return inner


def validate_instance_type(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, instances: BaseModel, *args, **kwargs):
        if instances:
            resource_type = instances[0].__class__
            if not all([isinstance(i, resource_type) for i in instances]):
                raise TypeError('All instances must be of the same type')
            if not issubclass(resource_type, DatalakeModel):
                raise TypeError('All instances must be of type DatalakeModel')
        return func(self, instances, *args, **kwargs)
    return wrapper


class AbstractDatalakeClient(AbstractClient):

    valid_filters = ["in", "contains", "gte", "lte"]

    def _validated_kwargs(self, resource_type: Type, **kwargs):
        valid_fields: List[str] = list(resource_type.__fields__.keys())

        valid_filter: Dict[str, str] = {
            key: value for key, value in kwargs.items()
            if key in valid_fields or
            any(f"{valid_field}__" in key for valid_field in valid_fields)
        }

        return valid_filter

    @abstractmethod
    def _get(self,
             resource_type: Type,
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
             resource_type: Type,
             limit_: int = 50,
             skip_: int = 0,
             sort: Union[List, str] = ['timestamp__desc'],
             group_id: Union[List, str] = [],
             group_fields: Union[List, str] = [],
             tzinfo: timezone = timezone(timedelta()),
             **kwargs) -> List[BaseModel]:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, count_func="None", *args, **kwargs)

    def raw_get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, get_func="_raw_get", count_func="None", *args, **kwargs)

    @abstractmethod
    def get_output(self, query: Query) -> List[Dict]:
        pass

    @abstractmethod
    def get_dataframe(self, resource_type: Type, freq="H", **kwargs) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_dataset(self, queries: List[Query]) -> pd.DataFrame:
        pass

    @abstractmethod
    def save(self, instances: List[BaseModel]) -> List[BaseModel]:
        pass

    @abstractmethod
    def save_dataframe(self, resource_type: Type, dataframe: pd.DataFrame) -> None:
        pass

    # Subject to incompatibility by implementation
    # Raw methods

    # def raw_save(self, instances: List[Dict], collection: str = "default") -> Dict:
    #     pass

    # def raw_get_dataframe
    # def raw_save_dataframe

    # @abstractmethod
    # def _raw_get(self,
    #              collection: str = 'default',
    #              limit_: int = 50,
    #              skip_: int = 0,
    #              sort: Union[List, str] = ['timestamp__desc'],
    #              group_id: Union[List, str] = [],
    #              group_fields: Union[List, str] = [],
    #              tzinfo: timezone = timezone(timedelta()),
    #              **kwargs) -> List[BaseModel]:
    #     pass

    # @abstractmethod
    # def raw_aggregate(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
    #     pass

    @abstractmethod
    def create_index(self, collection: str, index: list) -> None:
        pass

    # @abstractmethod
    # def list_collection_names(self) -> List[str]:
    #     pass

    # @abstractmethod
    # def get_unique_keys(self, collection: str) -> List[str]:
    #     pass

    # @abstractmethod
    # def get_values_for_key(self, collection: str, key: str) -> List[str]:
    #     pass