from splight_lib.models._v4.asset import Asset, AssetKind, AssetRelationship
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.base import (
    AttributeType,
    ResourceSummary,
    ValueType,
)
from splight_lib.models._v4.battery import Battery
from splight_lib.models._v4.bus import Bus
from splight_lib.models._v4.component import (
    DB_MODEL_TYPE_MAPPING,
    Component,
    ComponentObject,
    ComponentObjectInstance,
    ComponentType,
    CustomType,
    Endpoint,
    InputDataAddress,
    InputParameter,
    Output,
    Parameter,
    PrivacyPolicy,
    Routine,
    RoutineEvaluation,
    RoutineObject,
    RoutineObjectInstance,
    get_field_value,
)
from splight_lib.models._v4.data_address import DataAddresses as DataAddress
from splight_lib.models._v4.datalake import (
    AttributeDocument,
    Query,
    Records,
    SolutionOutputDocument,
)
from splight_lib.models._v4.datalake_base import SplightDatalakeBaseModel
from splight_lib.models._v4.external_grid import ExternalGrid
from splight_lib.models._v4.file import File
from splight_lib.models._v4.generator import Generator
from splight_lib.models._v4.grid import Grid
from splight_lib.models._v4.hub import HubComponent
from splight_lib.models._v4.hub_server import HubServer
from splight_lib.models._v4.line import Line
from splight_lib.models._v4.load import Load
from splight_lib.models._v4.metadata import Metadata
from splight_lib.models._v4.native import Boolean, Number, String
from splight_lib.models._v4.secret import Secret
from splight_lib.models._v4.segment import Segment
from splight_lib.models._v4.server import Server
from splight_lib.models._v4.slack_line import SlackLine
from splight_lib.models._v4.tag import Tag
from splight_lib.models._v4.transformer import Transformer

# from splight_lib.settings import SplightAPIVersion, api_settings

# TODO: Revert this change when possible
# if api_settings.API_VERSION != SplightAPIVersion.V4:
#     raise ImportError(
#         f"Unable to import models from this module when API_VERSION is not set to '{SplightAPIVersion.V4}'."
#     )


__all__ = [
    "Asset",
    "AssetRelationship",
    "Component",
    "RoutineObjectInstance",
    "RoutineObject",
    "RoutineEvaluation",
    "ComponentObject",
    "ComponentObjectInstance",
    "ComponentType",
    "CustomType",
    "Endpoint",
    "InputParameter",
    "Output",
    "PrivacyPolicy",
    "Routine",
    "SplightDatalakeBaseModel",
    "get_field_value",
    "Parameter",
    "DB_MODEL_TYPE_MAPPING",
    "Query",
    "Records",
    "AttributeDocument",
    "SolutionOutputDocument",
    "DataAddress",
    "InputDataAddress",
    "PipelineStep",
    "Trace",
    "File",
    "HubComponent",
    "HubServer",
    "Boolean",
    "Number",
    "String",
    "Secret",
    "Server",
    "Tag",
    "Metadata",
    "Attribute",
    "ResourceSummary",
    "AssetKind",
    "ValueType",
    "AttributeType",
    "Battery",
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
