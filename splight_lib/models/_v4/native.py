from datetime import datetime, timedelta, timezone
from typing import ClassVar, Literal

import pandas as pd
from pydantic import field_validator
from typing_extensions import Self

from splight_lib.models._v4.asset import Asset
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.datalake_base import SplightDatalakeBaseModel


class NativeOutput(SplightDatalakeBaseModel):
    asset: str | Asset
    attribute: str | Attribute
    output_format: str | None = None
    _schema_name: ClassVar[Literal["default"]] = "default"
    _output_format: ClassVar[str] = "default"

    @field_validator("output_format", mode="before")
    def set_output_format(cls, v) -> str:
        return cls._output_format

    @classmethod
    def get(
        cls, asset: str | Asset, attribute: str | Attribute, **params: dict
    ) -> list[Self]:
        return super()._get(
            [{"asset": asset, "attribute": attribute}], **params
        )

    @classmethod
    async def async_get(
        cls, asset: str | Asset, attribute: str | Attribute, **params: dict
    ) -> list[Self]:
        return await super()._async_get(
            [{"asset": asset, "attribute": attribute}], **params
        )

    @classmethod
    def get_dataframe(
        cls, asset: str | Asset, attribute: str | Attribute, **params: dict
    ) -> pd.DataFrame:
        df = super()._get_dataframe(
            [{"asset": asset, "attribute": attribute}], **params
        )
        df["output_format"] = cls._output_format
        return df

    @classmethod
    def latest(
        cls,
        asset: str | Asset,
        attribute: str | Attribute,
        expiration: timedelta = timedelta(hours=1),
    ) -> Self:
        from_timestamp = datetime.now(timezone.utc) - expiration
        result = cls.get(
            asset=asset,
            attribute=attribute,
            start=from_timestamp,
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


class SolutionOutputDocument(SplightDatalakeBaseModel):
    asset: str | Asset
    solution: str
    output: str
    value: bool | int | float | str

    _schema_name: ClassVar[Literal["solutions"]] = "solutions"

    @classmethod
    def get(
        cls, solution: str, output: str, asset: str, **params: dict
    ) -> list[Self]:
        solution_keys = [
            {"solution": solution, "output": output, "asset": asset}
        ]
        return super()._get(solution_keys, **params)

    @classmethod
    async def async_get(
        cls, solution: str, output: str, asset: str, **params: dict
    ) -> list[Self]:
        solution_keys = [
            {"solution": solution, "output": output, "asset": asset}
        ]
        return await super()._async_get(solution_keys, **params)

    @classmethod
    def get_dataframe(
        cls, solution: str, output: str, asset: str, **params: dict
    ) -> pd.DataFrame:
        solution_keys = [
            {"solution": solution, "output": output, "asset": asset}
        ]
        return super()._get_dataframe(solution_keys, **params)

    @classmethod
    def latest(
        cls,
        solution: str,
        output: str,
        asset: str,
        expiration: timedelta = timedelta(hours=1),
    ) -> Self:
        from_timestamp = datetime.now(timezone.utc) - expiration
        result = cls.get(
            solution=solution,
            output=output,
            asset=asset,
            start=from_timestamp,
            limit=1,
        )
        if result:
            return result[0]
        return None
