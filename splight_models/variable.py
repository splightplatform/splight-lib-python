import pandas as pd
from pydantic import Field
from typing import Dict, Union, Optional
from .asset import Asset
from .attribute import Attribute
from .datalake import DatalakeModel, RunnerDatalakeModel


class Variable(DatalakeModel):
    args: Optional[Dict] = None
    path: Optional[str] = None
    asset_id: Optional[str] = None
    attribute_id: Optional[str] = None


class ConnectorOutput(RunnerDatalakeModel):
    asset: Union[Asset, str]
    attribute: Union[Attribute, str]


class Number(ConnectorOutput):
    output_format: str = Field("Number", const=True)
    value: float


class String(ConnectorOutput):
    output_format: str = Field("String", const=True)
    value: str


class Boolean(ConnectorOutput):
    output_format: str = Field("Boolean", const=True)
    value: bool


class VariableDataFrame(pd.DataFrame):
    pass
