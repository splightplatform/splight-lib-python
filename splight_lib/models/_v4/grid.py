from splight_lib.models._v4.asset import AssetParams
from splight_lib.models._v4.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Grid(AssetParams, SplightDatabaseBaseModel):
    # Metadata
    max_allowed_disc_power: Metadata | None = None
    rag_enabled: Metadata | None = None
