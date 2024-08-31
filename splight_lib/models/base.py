import json
from datetime import datetime, timezone
from enum import auto
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Self, TypeVar

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from strenum import LowercaseStrEnum

from splight_lib.client.database import DatabaseClientBuilder
from splight_lib.client.database.abstract import AbstractDatabaseClient
from splight_lib.client.datalake import DatalakeClientBuilder
from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.models.datalake import DataRecords, DataRequest, Trace
from splight_lib.settings import settings


def datalake_model_serializer(data: Dict, default=str, **dumps_kwargs):
    new_data = {
        k: v if not isinstance(v, dict) else v["id"] for k, v in data.items()
    }
    return json.dumps(new_data, default=default, **dumps_kwargs)


FilePath = TypeVar("FilePath", str, Path)


class PrivacyPolicy(LowercaseStrEnum):
    PUBLIC = auto()
    PRIVATE = auto()


class ResourceSummary(BaseModel):
    id: str | None = None
    name: str


class SplightDatabaseBaseModel(BaseModel):
    _db_client: AbstractDatabaseClient = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._db_client = self.__get_database_client()

    @staticmethod
    def get_event_name(type_: str, action: str) -> str:
        return f"{type_.lower()}-{action.lower()}"

    def save(self):
        files_dict = self._get_model_files_dict()
        saved = self._db_client.save(
            self.__class__.__name__,
            self.model_dump(exclude_none=True, mode="json"),
            files=files_dict,
        )
        instance = self.model_validate(saved)
        for key, field in self.model_fields.items():
            setattr(self, key, getattr(instance, key))

    def delete(self):
        self._db_client.delete(
            resource_name=self.__class__.__name__, id=self.id
        )

    @classmethod
    def retrieve(cls, resource_id: str) -> "SplightDatabaseBaseModel":
        db_client = cls.__get_database_client()
        instance = db_client.get(
            resource_name=cls.__name__, id=resource_id, first=True
        )
        return cls.model_validate(instance) if instance else None

    @classmethod
    def list(cls, **params: Dict) -> List["SplightDatabaseBaseModel"]:
        db_client = cls.__get_database_client()
        instances = db_client.get(resource_name=cls.__name__, **params)
        instances = [cls.model_validate(item) for item in instances]
        return instances

    @staticmethod
    def __get_database_client() -> AbstractDatabaseClient:
        db_client = DatabaseClientBuilder.build(
            parameters={
                "base_url": settings.SPLIGHT_PLATFORM_API_HOST,
                "access_id": settings.SPLIGHT_ACCESS_ID,
                "secret_key": settings.SPLIGHT_SECRET_KEY,
            },
        )
        return db_client

    def _get_model_files_dict(self) -> Optional[Dict]:
        return None


class SplightDatalakeBaseModel(BaseModel):
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    _collection_name: ClassVar[str] = "DatalakeModel"
    _dl_client: AbstractDatalakeClient = PrivateAttr()

    model_config = ConfigDict(extra="ignore")

    @classmethod
    def get(cls, asset: str, attribute: str, **params: Dict) -> list[Self]:
        request = DataRequest[cls](
            from_timestamp=params.get("from_timestamp"),
            to_timestamp=params.get("to_timestamp"),
        )
        request.add_trace(Trace.from_address(asset, attribute))
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
