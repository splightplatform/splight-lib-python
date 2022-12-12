# TODO rename this file or move it to datalake
import pandas as pd
from pydantic import Field
from datetime import datetime, timezone
from typing import Dict, Union, Optional
from .asset import Asset
from .attribute import Attribute
from .datalake import DatalakeModel


# TODO remove Variable and VariableDataFrame
class Variable(DatalakeModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None
    args: Optional[Dict] = None
    path: Optional[str] = None
    asset_id: Optional[str] = None
    attribute_id: Optional[str] = None

    class Config:
        # pydantic
        validate_assignment = True

    class Meta:
        collection_name = "default"

    class SpecFields:
        # Fields to reconstruct Spec .fields
        pass


class VariableDataFrame(pd.DataFrame):
    pass


class NativeOutput(DatalakeModel):
    asset: Union[Asset, str]
    attribute: Union[Attribute, str]

    class Meta:
        collection_name = "default"


class Number(NativeOutput):
    output_format: str = Field("Number", const=True)
    value: float


class String(NativeOutput):
    output_format: str = Field("String", const=True)
    value: str


class Boolean(NativeOutput):
    output_format: str = Field("Boolean", const=True)
    value: bool
