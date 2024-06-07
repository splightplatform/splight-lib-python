import json
from datetime import datetime, timezone
from enum import auto
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, TypeVar

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from strenum import LowercaseStrEnum

from splight_lib.client.database import DatabaseClientBuilder
from splight_lib.client.database.abstract import AbstractDatabaseClient
from splight_lib.client.datalake import DatalakeClientBuilder
from splight_lib.client.datalake.abstract import AbstractDatalakeClient
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
    def get(
        cls, asset: str, attribute: str, **params: Dict
    ) -> List["SplightDatalakeBaseModel"]:
        dl_client = cls.__get_datalake_client()
        instances = dl_client.get(
            collection=cls._collection_name,
            match={"asset": asset, "attribute": attribute},
            **params,
        )
        instances = [
            cls.model_validate(
                {
                    "asset": asset,
                    "attribute": attribute,
                    "value": item["output"],
                    "timestamp": item["timestamp"],
                }
            )
            for item in instances
        ]
        return instances

    @classmethod
    async def async_get(
        cls, asset: str, attribute: str, **params: Dict
    ) -> List["SplightDatalakeBaseModel"]:
        dl_client = cls.__get_datalake_client()
        instances = await dl_client.async_get(
            collection=cls._collection_name,
            match={"asset": asset, "attribute": attribute},
            **params,
        )
        instances = [
            cls.model_validate(
                {
                    "asset": asset,
                    "attribute": attribute,
                    "value": item["output"],
                    "timestamp": item["timestamp"],
                }
            )
            for item in instances
        ]
        return instances

    def save(self):
        dl_client = self.__get_datalake_client()
        instance_dict = json.loads(self.model_dump_json())
        dl_client.save(
            collection=self._collection_name,
            instances=instance_dict,
        )

    async def async_save(self):
        dl_client = self.__get_datalake_client()

        await dl_client.async_save(
            collection=self._collection_name,
            instances=json.loads(self.model_dump_json()),
        )

    @classmethod
    def get_dataframe(
        cls, asset: str, attribute: str, **params: Dict
    ) -> pd.DataFrame:
        dl_client = cls.__get_datalake_client()
        df = dl_client.get_dataframe(
            match={"asset": asset, "attribute": attribute}, **params
        )
        return df

    @classmethod
    def save_dataframe(cls, df: pd.DataFrame):
        dl_client = cls.__get_datalake_client()
        dl_client.save_dataframe(
            df,
            collection=cls._collection_name,
        )

    def dict(self, *args, **kwargs) -> Dict:
        d = super().model_dump(*args, **kwargs)
        return {
            k: v["id"] if isinstance(v, dict) and "id" in v.keys() else v
            for k, v in d.items()
        }

    @staticmethod
    def __get_datalake_client() -> AbstractDatalakeClient:
        db_client = DatalakeClientBuilder.build(
            dl_client_type=settings.DL_CLIENT_TYPE,
            parameters={
                "base_url": settings.SPLIGHT_PLATFORM_API_HOST,
                "access_id": settings.SPLIGHT_ACCESS_ID,
                "secret_key": settings.SPLIGHT_SECRET_KEY,
                "buffer_size": settings.DL_BUFFER_SIZE,
                "buffer_timeout": settings.DL_BUFFER_TIMEOUT,
            },
        )
        return db_client
