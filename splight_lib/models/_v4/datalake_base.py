from datetime import datetime, timezone
from typing import ClassVar, Dict

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

from splight_lib.client.datalake.v4.builder import get_datalake_client
from splight_lib.client.datalake.v4.models import (
    DefaultKeys,
    SolutionKeys,
    TransitionReadSerializer,
    TransitionWriteSerializer,
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
        dl_client = get_datalake_client()
        request = request.model_dump(mode="json")
        response = dl_client.get(request)
        return response["results"]

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
        dl_client = get_datalake_client()
        request = request.model_dump(mode="json")
        response = await dl_client.async_get(request)
        return response["results"]

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
        dl_client = get_datalake_client()
        request = request.model_dump(mode="json")
        response = dl_client.get(request)
        df = pd.DataFrame(response["results"])
        if not df.empty:
            df.index = df["timestamp"]
            df.drop(columns="timestamp", inplace=True)
        return df

    @classmethod
    def __to_read_request(
        cls,
        key_entries: list[dict[str, str]],
        **params: dict,
    ) -> TransitionReadSerializer:
        _schema_name = cls._schema_name
        schema = DefaultKeys if _schema_name == "default" else SolutionKeys
        return TransitionReadSerializer(
            keys=schema.load(entries=key_entries),
            **params,
        )

    def save(self) -> None:
        dl_client = get_datalake_client()
        record = self.__to_write_request()
        dl_client.save(record.model_dump(mode="json"))

    async def async_save(self) -> None:
        dl_client = get_datalake_client()
        record = self.__to_write_request()
        await dl_client.async_save(record.model_dump(mode="json"))

    @classmethod
    def save_dataframe(cls, df: pd.DataFrame):
        df = _fix_dataframe_timestamp(df)
        instances = df.to_dict("records")
        records = TransitionWriteSerializer(
            schema_name=cls._schema_name,
            records=instances,
        )
        dl_client = get_datalake_client()
        dl_client.save(records.model_dump(mode="json"))

    def dict(self, *args, **kwargs) -> Dict:
        d = super().model_dump(*args, **kwargs)
        return {
            k: v["id"] if isinstance(v, dict) and "id" in v.keys() else v
            for k, v in d.items()
        }

    def __to_write_request(self) -> TransitionWriteSerializer:
        return TransitionWriteSerializer(
            schema_name=self._schema_name,
            records=[self.model_dump(mode="json")],
        )


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
