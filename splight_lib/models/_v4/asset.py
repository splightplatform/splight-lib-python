from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.base import AssetKind, AssetParams, ResourceSummary
from splight_lib.models._v4.exceptions import InvalidOperation
from splight_lib.models._v4.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class AssetRelationship(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    related_asset_kind: AssetKind | None = None
    asset: ResourceSummary | None = None
    related_asset: ResourceSummary | None = None

    def save(self) -> None:
        raise InvalidOperation("save")

    def delete(self) -> None:
        raise InvalidOperation("delete")

    def set(self, asset_id: str) -> None:
        self._db_client.operate(
            "set-asset-relationship",
            instance={
                "relationship": self.id,
                "related_asset": asset_id,
            },
        )


class Asset(AssetParams, SplightDatabaseBaseModel):
    attributes: list[Attribute] | None = None
    metadata: list[Metadata] | None = None
    related_to: list[AssetRelationship] | None = None
    related_from: list[AssetRelationship] | None = None
