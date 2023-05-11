from splight_lib.models.base import SplightDatalakeBaseModel
from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from pydantic import Field
from typing import Union


class NativeOutput(SplightDatalakeBaseModel):
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
