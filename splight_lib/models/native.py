from typing import ClassVar, Dict, List, Optional, Union

import pandas as pd
from pydantic import validator

from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.base import SplightDatalakeBaseModel


class NativeOutput(SplightDatalakeBaseModel):
    asset: Union[Asset, str]
    attribute: Union[Attribute, str]
    output_format: Optional[str] = None
    _collection_name: ClassVar[str] = "default"
    _output_format: ClassVar[str] = "default"

    @validator("output_format", always=True)
    def set_output_format(cls, v):
        return cls._output_format

    @classmethod
    def get(cls, **params: Dict) -> List["NativeOutput"]:
        params["output_format"] = cls._output_format
        return super().get(**params)

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
    _output_format: ClassVar[str] = "Number"


class String(NativeOutput):
    value: str
    _output_format: ClassVar[str] = "String"


class Boolean(NativeOutput):
    value: bool
    _output_format: ClassVar[str] = "Boolean"
