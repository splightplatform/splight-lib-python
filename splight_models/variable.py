# TODO rename this file or move it to datalake
from pydantic import Field
from typing import Union
from .asset import Asset
from .attribute import Attribute
from .datalake import DatalakeModel


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
