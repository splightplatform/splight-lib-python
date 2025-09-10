from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, TypeVar

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

from splight_lib.models._v4.datalake import (
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
    _model_type: ClassVar[str] = ...

    model_config = ConfigDict(extra="ignore")

    @classmethod
    def _get(
        cls,
        filters: dict[str, str],
        extra_pipeline: list[dict[str, Any]] = [],
        **params: dict,
    ) -> list[Self]:
        request = _to_data_request(
            cls,
            filters,
            extra_pipeline,
            **params,
        )
        return request.apply()

    @classmethod
    async def _async_get(
        cls,
        filters: dict[str, str],
        extra_pipeline: list[dict[str, Any]] = [],
        **params: dict,
    ) -> list[Self]:
        request = _to_data_request(cls, filters, extra_pipeline, **params)
        instances = await request.async_apply()
        return instances

    @classmethod
    def _get_dataframe(
        cls,
        filters: dict[str, str],
        extra_pipeline: list[dict[str, Any]] = [],
        **params: dict,
    ) -> pd.DataFrame:
        request = _to_data_request(
            cls,
            filters,
            extra_pipeline,
            **params,
        )
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
    filters: dict[str, str],
    extra_pipeline: list[dict[str, Any]] = [],
    **params: Dict,
) -> DataRequest:
    if not isinstance(extra_pipeline, list):
        raise ValueError("extra_pipeline must be a list of dicts")
    model_type = model_class._model_type
    collection = (
        "default" if model_type == "attribute_document" else "solutions"
    )
    request = DataRequest[model_class](
        collection=collection,
        from_timestamp=params.get("from_timestamp"),
        to_timestamp=params.get("to_timestamp"),
    )

    if model_type == "attribute_document":
        trace = Trace.from_address(**filters)
    elif model_type == "solution_output_document":
        trace = Trace.from_so_filter(**filters)
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
