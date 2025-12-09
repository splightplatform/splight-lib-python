from datetime import datetime, timezone
from typing import ClassVar, Dict

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

from splight_lib.models._v4.datalake import (
    DataReadRequest,
    DataWriteRequest,
    DefaultKeys,
    DefaultRecords,
    SolutionKeys,
    SolutionRecords,
)


class SplightDatalakeBaseModel(BaseModel):
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    _schema_name: ClassVar[str] = "DatalakeModel"

    model_config = ConfigDict(extra="ignore")

    @classmethod
    def _get(
        cls,
        key_entries: list[dict[str, str]],
        **params: dict,
    ) -> list[Self]:
        request = cls.__to_read_request(
            key_entries,
            **params,
        )
        return request.apply()

    @classmethod
    async def _async_get(
        cls,
        key_entries: list[dict[str, str]],
        **params: dict,
    ) -> list[Self]:
        request = cls.__to_read_request(
            key_entries,
            **params,
        )
        return await request.async_apply()

    @classmethod
    def _get_dataframe(
        cls,
        key_entries: list[dict[str, str]],
        **params: dict,
    ) -> pd.DataFrame:
        request = cls.__to_read_request(
            key_entries,
            **params,
        )
        results = request.apply()
        df = pd.DataFrame(results)
        if not df.empty:
            df.index = df["timestamp"]
            df.drop(columns="timestamp", inplace=True)
        return df

    @classmethod
    def __to_read_request(
        cls,
        key_entries: list[dict[str, str]],
        **params: dict,
    ) -> DataReadRequest:
        _schema_name = cls._schema_name
        schema = DefaultKeys if _schema_name == "default" else SolutionKeys
        return DataReadRequest(
            keys=schema.load(entries=key_entries),
            **params,
        )

    @classmethod
    def __to_write_request(
        cls,
        data_points: list[dict[str, str]],
    ) -> DataWriteRequest:
        _schema_name = cls._schema_name
        schema = (
            DefaultRecords if _schema_name == "default" else SolutionRecords
        )
        return DataWriteRequest(
            records=schema.load(data_points=data_points),
        )

    def save(self) -> None:
        request = self.__to_write_request(
            data_points=[self.model_dump(mode="json")]
        )
        request.apply()

    async def async_save(self) -> None:
        request = self.__to_write_request(
            data_points=[self.model_dump(mode="json")]
        )
        await request.async_apply()

    @classmethod
    def save_dataframe(cls, df: pd.DataFrame):
        df = _fix_dataframe_timestamp(df)
        instances = df.to_dict("records")
        request = cls.__to_write_request(data_points=instances)
        request.apply()

    def dict(self, *args, **kwargs) -> Dict:
        d = super().model_dump(*args, **kwargs)
        return {
            k: v["id"] if isinstance(v, dict) and "id" in v.keys() else v
            for k, v in d.items()
        }


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
