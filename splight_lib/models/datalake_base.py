import json
from datetime import datetime, timezone
from typing import ClassVar, Dict, Self

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.datalake import DataRecords, DataRequest, Trace


def datalake_model_serializer(data: Dict, default=str, **dumps_kwargs):
    new_data = {
        k: v if not isinstance(v, dict) else v["id"] for k, v in data.items()
    }
    return json.dumps(new_data, default=default, **dumps_kwargs)


class SplightDatalakeBaseModel(BaseModel):
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    _collection_name: ClassVar[str] = "DatalakeModel"

    model_config = ConfigDict(extra="ignore")

    @classmethod
    def get(
        cls, asset: str | Asset, attribute: str, **params: Dict
    ) -> list[Self]:
        asset_id = asset.id if isinstance(asset, Asset) else asset
        attribute_id = (
            attribute.id if isinstance(attribute, Attribute) else attribute
        )
        request = DataRequest[cls](
            from_timestamp=params.get("from_timestamp"),
            to_timestamp=params.get("to_timestamp"),
        )
        request.add_trace(Trace.from_address(asset_id, attribute_id))
        return request.apply()

    @classmethod
    async def async_get(
        cls, asset: str, attribute: str, **params: Dict
    ) -> list[Self]:
        request = DataRequest[cls](
            from_timestamp=params.get("from_timestamp"),
            to_timestamp=params.get("to_timestamp"),
        )
        request.add_trace(Trace.from_address(asset, attribute))
        instances = await request.async_apply()
        return instances

    @classmethod
    def get_dataframe(
        cls, asset: str, attribute: str, **params: Dict
    ) -> pd.DataFrame:
        request = DataRequest[cls](
            from_timestamp=params.get("from_timestamp"),
            to_timestamp=params.get("to_timestamp"),
        )
        request.add_trace(Trace.from_address(asset, attribute))
        instances = request.apply()
        df = pd.DataFrame([instance.dict() for instance in instances])
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
