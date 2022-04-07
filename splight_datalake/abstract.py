from client import AbstractClient
from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List, Dict
from datetime import datetime
from splight_models import Variable, VariableDataFrame


class AbstractDatalakeClient(AbstractClient):

    @abstractmethod
    def save(self, resource_type: Type, instances: List[BaseModel], collection: str = "default") -> List[BaseModel]:
        pass

    @abstractmethod
    def get(self,
            resource_type: Type,
            collection: str = "default",
            from_: datetime = None,
            to_: datetime = None,
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

    def _validated_kwargs(self, resource_type: Type, **kwargs):
        valid_fields: List[str] = list(f"{key}__" for key in resource_type.__fields__.keys())
        valid_filter: Dict[str, str] = {key: value for key, value in kwargs.items() if any(key.startswith(s) for s in valid_fields)}
        kwargs = super()._validated_kwargs(resource_type, **kwargs)
        return {**kwargs, **valid_filter}
