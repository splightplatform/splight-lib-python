from venv import create
from client import AbstractClient
from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List, Dict
from datetime import datetime
from splight_models import Variable, VariableDataFrame


class AbstractDatalakeClient(AbstractClient):

    valid_filters = ["in", "contains", "gte", "lte"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def save(self, resource_type: Type, instances: List[BaseModel], collection: str = "default") -> List[BaseModel]:
        pass

    @abstractmethod
    def get(self,
            resource_type: Type,
            collection: str = "default",
            first: bool = False,
            limit_: int = 50,
            skip_: int = 0,
            **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def get_dataframe(self, variable: Variable, freq="H", collection: str = "default") -> VariableDataFrame:
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

    @abstractmethod
    def get_components_sizes_gb(self, start: datetime = None, end: datetime = None) -> Dict:
        pass
    
    def _validated_kwargs(self, resource_type: Type, **kwargs):
        valid_fields: List[str] = list(resource_type.__fields__.keys())

        valid_filter: Dict[str, str] = {
            key: value for key, value in kwargs.items()
            if key in valid_fields or
            any(f"{valid_field}__" in key for valid_field in valid_fields)
        }

        return valid_filter