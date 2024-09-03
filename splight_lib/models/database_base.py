from enum import auto
from pathlib import Path
from typing import Dict, List, Optional, TypeVar

from pydantic import BaseModel, PrivateAttr
from strenum import LowercaseStrEnum

from splight_lib.client.database import DatabaseClientBuilder
from splight_lib.client.database.abstract import AbstractDatabaseClient
from splight_lib.settings import settings

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
