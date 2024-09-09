from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Self, TypeVar

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.datalake import (
    DataRecords,
    DataRequest,
    PipelineStep,
    Trace,
)


class SplightDatalakeBaseModel(BaseModel):
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    _collection_name: ClassVar[str] = "DatalakeModel"

    model_config = ConfigDict(extra="ignore")

    @classmethod
    def get(
        cls,
        asset: str | Asset,
        attribute: str | Attribute,
        extra_pipeline: list[dict[str, Any]] = [],
        **params: Dict,
    ) -> list[Self]:
        request = _to_data_request(
            cls, asset, attribute, extra_pipeline, **params
        )
        return request.apply()

    @classmethod
    async def async_get(
        cls,
        asset: str | Asset,
        attribute: str | Attribute,
        extra_pipeline: list[dict[str, Any]] = [],
        **params: Dict,
    ) -> list[Self]:
        request = _to_data_request(
            cls, asset, attribute, extra_pipeline, **params
        )
        instances = await request.async_apply()
        return instances

    @classmethod
    def get_dataframe(
        cls,
        asset: str | Asset,
        attribute: str | Attribute,
        extra_pipeline: list[dict[str, Any]] = [],
        **params: Dict,
    ) -> pd.DataFrame:
        request = _to_data_request(
            cls, asset, attribute, extra_pipeline, **params
        )
        instances = request.apply()
        df = pd.DataFrame([instance.dict() for instance in instances])
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
        records = DataRecords(
            collection=cls._collection_name,
            records=instances,
        )
        records.apply()

    def dict(self, *args, **kwargs) -> Dict:
        d = super().model_dump(*args, **kwargs)
        return {
            k: v["id"] if isinstance(v, dict) and "id" in v.keys() else v
            for k, v in d.items()
        }

    def _to_record(self) -> DataRecords:
        return DataRecords(
            collection=self._collection_name,
            records=[self.model_dump(mode="json")],
        )


def _to_data_request(
    model_class: TypeVar("T"),
    asset: str | Asset,
    attribute: str | Attribute,
    extra_pipeline: list[dict[str, Any]] = [],
    **params: Dict,
) -> DataRequest:
    if not isinstance(extra_pipeline, list):
        raise ValueError("extra_pipeline must be a list of dicts")
    request = DataRequest[model_class](
        from_timestamp=params.get("from_timestamp"),
        to_timestamp=params.get("to_timestamp"),
    )
    trace = Trace.from_address(asset, attribute)
    for step in extra_pipeline:
        trace.add_step(PipelineStep.from_dict(step))
    request.add_trace(trace)
    return request


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
