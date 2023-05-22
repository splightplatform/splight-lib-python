import json
from datetime import datetime, timezone
from typing import ClassVar, Dict, List, Optional, Set, Tuple

import pandas as pd
from pydantic import BaseModel, Field, PrivateAttr
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


class SplightDatabaseBaseModel(BaseModel):
    _db_client: AbstractDatabaseClient = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._db_client = self.__get_database_client()

    @staticmethod
    def get_event_name(type_: str, action: str) -> str:
        return f"{type_.lower()}-{action.lower()}"

    def save(self):
        saved = self._db_client.save(
            self.__class__.__name__, self.dict(exclude_none=True)
        )
        if not self.id:
            self.id = saved["id"]

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
        return cls.parse_obj(instance) if instance else None

    @classmethod
    def list(cls, **params: Dict) -> List["SplightDatabaseBaseModel"]:
        db_client = cls.__get_database_client()
        instances = db_client.get(resource_name=cls.__name__, **params)
        instances = [cls.parse_obj(item) for item in instances]
        return instances

    @staticmethod
    def __get_database_client() -> AbstractDatabaseClient:
        db_client = DatabaseClientBuilder.build(
            local=settings.LOCAL_ENVIRONMENT,
            parameters={
                "path": settings.CURRENT_DIR,
                "base_url": settings.SPLIGHT_PLATFORM_API_HOST,
                "access_id": settings.SPLIGHT_ACCESS_ID,
                "secret_key": settings.SPLIGHT_SECRET_KEY,
            },
        )
        return db_client


class SplightDatalakeBaseModel(BaseModel):
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None
    _collection_name: ClassVar[str] = "DatalakeModel"
    _dl_client: AbstractDatalakeClient = PrivateAttr()

    class Config:
        json_dumps = datalake_model_serializer

    def __init__(self, **data):
        super().__init__(**data)
        self._dl_client = self.__get_datalake_client()

    @classmethod
    def get(cls, **params: Dict) -> List["SplightDatalakeBaseModel"]:
        dl_client = cls.__get_datalake_client()
        instances = dl_client.get(
            resource_name=cls.__name__,
            collection=cls._collection_name,
            **params,
        )
        instances = [cls.parse_obj(item) for item in instances]
        return instances

    @classmethod
    def get_dataframe(cls, **params: Dict) -> pd.DataFrame:
        dl_client = cls.__get_datalake_client()
        df = dl_client.get_dataframe(
            resource_name=cls.__name__,
            collection=cls._collection_name,
            **params,
        )
        return df

    def save(self):
        self._dl_client.save(
            collection=self._collection_name,
            instances=json.loads(self.json()),
        )

    @classmethod
    def save_dataframe(cls, dataframe: pd.DataFrame):
        dl_client = cls.__get_datalake_client()
        dl_client.save_dataframe(
            collection=cls._collection_name, dataframe=dataframe
        )

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        return {
            k: v["id"] if isinstance(v, dict) and "id" in v.keys() else v
            for k, v in d.items()
        }

    @classmethod
    def create_indexes(cls, parameters: List[Dict]):
        indices: Set[Tuple[str, int]] = set(
            [
                ("output_format", 1),
                ("instance_id", 1),
                ("instance_type", 1),
                ("asset", 1),
                ("attribute", 1),
                ("timestamp", -1),
            ]
        )
        for param in parameters:
            if param["filterable"]:
                indices.add((param["name"], 1))
        indices = list(indices)
        dl_client = cls.__get_datalake_client()
        dl_client.create_index(cls._collection_name, indices)

    @staticmethod
    def __get_datalake_client() -> AbstractDatalakeClient:
        db_client = DatalakeClientBuilder.build(
            local=settings.LOCAL_ENVIRONMENT,
            parameters={
                "path": settings.CURRENT_DIR,
                "base_url": settings.SPLIGHT_PLATFORM_API_HOST,
                "access_id": settings.SPLIGHT_ACCESS_ID,
                "secret_key": settings.SPLIGHT_SECRET_KEY,
            },
        )
        return db_client
