from typing import ClassVar, Dict, List, Literal, Optional, Union

import pandas as pd
from pydantic import field_validator

from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.base import SplightDatalakeBaseModel


class NativeOutput(SplightDatalakeBaseModel):
    asset: Union[Asset, str]
    attribute: Union[Attribute, str]
    output_format: Optional[str] = None
    _collection_name: ClassVar[str] = "default"
    _output_format: ClassVar[str] = "default"

    @field_validator("output_format", mode="before")
    def set_output_format(cls, v):
        return cls._output_format

    @classmethod
    def get(cls, **params: Dict) -> List["NativeOutput"]:
        params["output_format"] = cls._output_format
        return super().get(**params)

    @classmethod
    async def async_get(cls, **params: Dict) -> List["NativeOutput"]:
        params["output_format"] = cls._output_format
        return await super().async_get(**params)

    @classmethod
    def get_dataframe(cls, **params: Dict) -> pd.DataFrame:
        params["output_format"] = cls._output_format
        return super().get_dataframe(**params)

    @classmethod
    def save_dataframe(cls, dataframe: pd.DataFrame):
        dataframe["output_format"] = cls._output_format
        super().save_dataframe(dataframe)


class Number(NativeOutput):
    value: float
    output_format: Literal["Number"] = "Number"
    _output_format: ClassVar[str] = "Number"


class String(NativeOutput):
    value: str
    output_format: Literal["String"] = "String"
    _output_format: ClassVar[str] = "String"


class Boolean(NativeOutput):
    value: bool
    output_format: Literal["Boolean"] = "Boolean"
    _output_format: ClassVar[str] = "Boolean"
