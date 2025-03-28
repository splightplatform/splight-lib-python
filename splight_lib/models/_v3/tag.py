from splight_lib.models._v3.database_base import SplightDatabaseBaseModel


class Tag(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
