from splight_lib.models.v3.database_base import SplightDatabaseBaseModel


class Tag(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
