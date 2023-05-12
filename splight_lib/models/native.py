from typing import Optional, Union

from pydantic import Field, PrivateAttr
from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.base import SplightDatalakeBaseModel


class NativeOutput(SplightDatalakeBaseModel):
    asset: Union[Asset, str]
    attribute: Union[Attribute, str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._collection_name = "default"


class Number(NativeOutput):
    output_format: str = Field("Number", const=True)
    value: float


class String(NativeOutput):
    output_format: str = Field("String", const=True)
    value: str


class Boolean(NativeOutput):
    output_format: str = Field("Boolean", const=True)
    value: bool
