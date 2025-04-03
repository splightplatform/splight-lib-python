from splight_lib.models.database import SplightDatabaseBaseModel


class Tag(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
