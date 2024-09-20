from typing import Self

from splight_lib.models.database_base import SplightDatabaseBaseModel


class Secret(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    value: str

    @classmethod
    def decrypt(cls, name: str) -> Self:
        db_client = cls._SplightDatabaseBaseModel__get_database_client()
        response = db_client.operate(
            resource_name="decrypt-secret",
            instance={"name": name},
        )
        return cls.model_validate(response)
