from splight_lib.models import Asset, AssetParams
from splight_lib.models.database_base import SplightDatabaseBaseModel


class SlackLine(AssetParams, SplightDatabaseBaseModel):
    bus_from: None | Asset
    bus_to: None | Asset
    grid: None | Asset
