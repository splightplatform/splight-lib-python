from datetime import datetime, timezone
from typing import Dict, TypeVar

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

from splight_lib.models._v4.asset import Asset
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.datalake import AttributeDocument, Query, Records

T = TypeVar("T")


class SplightDatalakeBaseModel(BaseModel):
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    model_config = ConfigDict(extra="ignore")

    @classmethod
    def get(
        cls,
        asset: str | Asset,
        attribute: str | Attribute,
        **params: Dict,
    ) -> list[Self]:
        request = _to_query(AttributeDocument, asset, attribute, **params)
        return request.apply()

    @classmethod
    async def async_get(
        cls,
        asset: str | Asset,
        attribute: str | Attribute,
        **params: Dict,
    ) -> list[Self]:
        request = _to_query(AttributeDocument, asset, attribute, **params)
        instances = await request.async_apply()
        return instances

    @classmethod
    def get_dataframe(
        cls,
        asset: str | Asset,
        attribute: str | Attribute,
        **params: Dict,
    ) -> pd.DataFrame:
        request = _to_query(AttributeDocument, asset, attribute, **params)
        instances = request.apply()
        df = pd.DataFrame([instance.model_dump() for instance in instances])
        if not df.empty:
            df.index = df["timestamp"]
            df.drop(columns="timestamp", inplace=True)
        return df

    def save(self) -> None:
        records = self._to_record()
        records.apply()

    async def async_save(self) -> None:
        records = self._to_record()
        await records.async_apply()

    @classmethod
    def save_dataframe(cls, df: pd.DataFrame):
        df = _fix_dataframe_timestamp(df)
        instances = df.to_dict("records")
        records = Records[AttributeDocument](
            records=instances,
        )
        records.apply()

    def dict(self, *args, **kwargs) -> Dict:
        d = super().model_dump(*args, **kwargs)
        return {
            k: v["id"] if isinstance(v, dict) and "id" in v.keys() else v
            for k, v in d.items()
        }

    def _to_record(self) -> Records:
        return Records[AttributeDocument](
            records=[self.model_dump(mode="json")],
        )


def _to_query(
    model_class: T,
    asset: str | Asset,
    attribute: str | Attribute,
    **params: Dict,
) -> Query:
    attribute_id = (
        attribute if isinstance(attribute, str) else str(attribute.id)
    )
    query = Query[model_class](
        start_date=params.get("from_timestamp"),
        end_date=params.get("to_timestamp"),
        attributes=[attribute_id],
    )
    return query


def _fix_dataframe_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    if df["timestamp"][0].tz is None:
        df["timestamp"] = df["timestamp"].apply(
            lambda x: x.tz_localize(tz="UTC").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
    else:
        df["timestamp"] = df["timestamp"].apply(
            lambda x: x.tz_convert(tz="UTC").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
    return df
