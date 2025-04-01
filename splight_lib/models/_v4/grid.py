from splight_lib.models._v4.base import AssetParams, Metadata
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Grid(AssetParams, SplightDatabaseBaseModel):
    # Metadata
    max_allowed_disc_power: Metadata | None = None
