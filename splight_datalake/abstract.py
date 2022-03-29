import pandas as pd
from client import AbstractClient
from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List, Optional
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
