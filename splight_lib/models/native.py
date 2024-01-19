from typing import ClassVar, Dict, List, Literal, Optional, Union

from datetime import datetime, timedelta
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

    def latest(self, expiration: timedelta):
        from_timestamp = datetime.utcnow() - expiration
        result = self.get(
            asset=self.asset,
            attribute=self.attribute,
            from_timestamp=from_timestamp,
            limit=1,
        )
        if result:
            return result[0]
        return None


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
