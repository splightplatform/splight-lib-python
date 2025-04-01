from splight_lib.models.database_base import SplightDatabaseBaseModel


class Tag(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
