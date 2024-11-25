from splight_lib.models import Asset, AssetParams
from splight_lib.models.database_base import SplightDatabaseBaseModel


class SlackGenerator(AssetParams, SplightDatabaseBaseModel):
    bus: None | Asset
    grid: None | Asset
