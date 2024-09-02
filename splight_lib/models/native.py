from datetime import datetime, timedelta, timezone
from typing import ClassVar, Literal, Self

import pandas as pd
from pydantic import field_validator

from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.datalake_base import SplightDatalakeBaseModel


class NativeOutput(SplightDatalakeBaseModel):
    asset: str | Asset
    attribute: str | Attribute
    output_format: str | None = None
    _collection_name: ClassVar[str] = "default"
    _output_format: ClassVar[str] = "default"

    @field_validator("output_format", mode="before")
    def set_output_format(cls, v) -> str:
        return cls._output_format

    @classmethod
    def get(
        cls, asset: str | Asset, attribute: str | Attribute, **params: dict
    ) -> list[Self]:
        return super().get(asset, attribute, **params)

    @classmethod
    async def async_get(
        cls, asset: str | Asset, attribute: str | Attribute, **params: dict
    ) -> list[Self]:
        return await super().async_get(asset, attribute, **params)

    @classmethod
    def get_dataframe(
        cls, asset: str | Asset, attribute: str | Attribute, **params: dict
    ) -> pd.DataFrame:
        df = super().get_dataframe(asset, attribute, **params)
        df["output_format"] = cls._output_format
        return df

    @classmethod
    def latest(
        cls,
        asset: str | Asset,
        attribute: str | Attribute,
        expiration: timedelta | None = None,
    ) -> Self:
        from_timestamp = None
        if expiration:
            from_timestamp = datetime.now(timezone.utc) - expiration
        result = cls.get(
            asset=asset,
            attribute=attribute,
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
