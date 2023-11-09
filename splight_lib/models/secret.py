from typing import Optional

from splight_lib.models.base import SplightDatabaseBaseModel


class Secret(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    value: str

    @classmethod
    def decrypt(cls, name: str):
        db_client = cls._SplightDatabaseBaseModel__get_database_client()
        response = db_client.operate(
            resource_name="decrypt-secret",
            instance={"name": name},
        )
        return cls.model_validate(response)
