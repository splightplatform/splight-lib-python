from splight_lib.models._v4.asset import Asset
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.base import (
    AssetKind,
    AssetRelationship,
    AttributeType,
    ResourceSummary,
    ValueType,
)
from splight_lib.models._v4.bus import Bus
from splight_lib.models._v4.external_grid import ExternalGrid
from splight_lib.models._v4.generator import Generator
from splight_lib.models._v4.grid import Grid
from splight_lib.models._v4.line import Line
from splight_lib.models._v4.load import Load
from splight_lib.models._v4.metadata import Metadata
from splight_lib.models._v4.segment import Segment
from splight_lib.models._v4.slack_line import SlackLine
from splight_lib.models._v4.transformer import Transformer
from splight_lib.settings import SplightAPIVersion, api_settings

if api_settings.API_VERSION != SplightAPIVersion.V4:
    raise ImportError(
        f"Unable to import models from this module when API_VERSION is not set to '{SplightAPIVersion.V4}'."
    )


__all__ = [
    "Asset",
    "AssetRelationship",
    "Metadata",
    "Attribute",
    "ResourceSummary",
    "AssetKind",
    "ValueType",
    "AttributeType",
    "Bus",
    "ExternalGrid",
    "Generator",
    "Grid",
    "Line",
    "Load",
    "Segment",
    "SlackLine",
    "Transformer",
]
