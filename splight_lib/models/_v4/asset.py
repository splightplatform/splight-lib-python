from splight_lib.models._v4.base import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database import SplightDatabaseBaseModel


class Asset(AssetParams, SplightDatabaseBaseModel):
    attributes: list[Attribute] = []
    metadata: list[Metadata] = []
