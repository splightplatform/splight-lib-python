from typing import Dict, List

from pydantic import BaseModel, PrivateAttr
from splight_abstract.database import AbstractDatabaseClient
from splight_lib.client.database import DatabaseClientBuilder
from splight_lib.settings import settings


class SplightDatabaseBaseModel(BaseModel):

    _db_client: AbstractDatabaseClient = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._db_client = self.__get_database_client()

    @staticmethod
    def get_event_name(type: str, action: str) -> str:
        return f"{type.lower()}-{action.lower()}"

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
