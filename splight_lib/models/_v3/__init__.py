# from splight_lib.settings import SplightAPIVersion, api_settings

# TODO: Revert this change when possible
# if api_settings.API_VERSION != SplightAPIVersion.V3:
#     raise ImportError(
#         f"Unable to import models from this module when API_VERSION is not set to '{SplightAPIVersion.V3}'."
#     )

from splight_lib.models._v3.actions import Action, SetPoint
from splight_lib.models._v3.alert import Alert, AlertItem
from splight_lib.models._v3.asset import (
    Asset,
    AssetKind,
    AssetParams,
    AssetRelationship,
)
from splight_lib.models._v3.attribute import Attribute
from splight_lib.models._v3.bus import Bus
from splight_lib.models._v3.component import (
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
from splight_lib.models._v3.dashboard import (
    AdvancedFilter,
    Chart,
    ChartItem,
    Dashboard,
    DashboardActionListChart,
    DashboardAlertEventsChart,
    DashboardAlertListChart,
    DashboardAssetListChart,
    DashboardBarChart,
    DashboardBarGaugeChart,
    DashboardCommandListChart,
    DashboardGaugeChart,
    DashboardHistogramChart,
    DashboardImageChart,
    DashboardStatChart,
    DashboardTableChart,
    DashboardTextChart,
    DashboardTimeseriesChart,
    Filter,
    Tab,
)
from splight_lib.models._v3.data_address import DataAddresses as DataAddress
from splight_lib.models._v3.datalake import DataRequest, PipelineStep, Trace
from splight_lib.models._v3.datalake_base import SplightDatalakeBaseModel
from splight_lib.models._v3.external_grid import ExternalGrid
from splight_lib.models._v3.file import File
from splight_lib.models._v3.function import Function, FunctionItem, QueryFilter
from splight_lib.models._v3.generator import Generator
from splight_lib.models._v3.grid import Grid
from splight_lib.models._v3.hub import HubComponent
from splight_lib.models._v3.hub_server import HubServer
from splight_lib.models._v3.inverter import Inverter
from splight_lib.models._v3.line import Line
from splight_lib.models._v3.metadata import Metadata
from splight_lib.models._v3.native import Boolean, Number, String
from splight_lib.models._v3.secret import Secret
from splight_lib.models._v3.segment import Segment
from splight_lib.models._v3.server import Server
from splight_lib.models._v3.slack_generator import SlackGenerator
from splight_lib.models._v3.slack_line import SlackLine
from splight_lib.models._v3.tag import Tag
from splight_lib.models._v3.three_winding_transformer import (
    ThreeWindingTransformer,
)
from splight_lib.models._v3.transformer import Transformer

__all__ = [
    "Action",
    "AdvancedFilter",
    "Alert",
    "AlertItem",
    "Asset",
    "AssetParams",
    "AssetRelationship",
    "Tag",
    "AssetKind",
    "Attribute",
    "Boolean",
    "Chart",
    "DashboardActionListChart",
    "DashboardAlertEventsChart",
    "DashboardAlertListChart",
    "DashboardAssetListChart",
    "DashboardBarChart",
    "DashboardBarGaugeChart",
    "DashboardCommandListChart",
    "DashboardGaugeChart",
    "DashboardHistogramChart",
    "DashboardImageChart",
    "DashboardStatChart",
    "DashboardTableChart",
    "DashboardTextChart",
    "DashboardTimeseriesChart",
    "DataAddress",
    "ChartItem",
    "Component",
    "ComponentObject",
    "ComponentObjectInstance",
    "ComponentType",
    "CustomType",
    "Endpoint",
    "Output",
    "InputParameter",
    "InputDataAddress",
    "PrivacyPolicy",
    "Routine",
    "get_field_value",
    "SplightDatalakeBaseModel",
    "DB_MODEL_TYPE_MAPPING",
    "Parameter",
    "Dashboard",
    "DataRequest",
    "File",
    "Filter",
    "Function",
    "FunctionItem",
    "HubComponent",
    "HubServer",
    "QueryFilter",
    "Metadata",
    "Number",
    "PipelineStep",
    "Bus",
    "ExternalGrid",
    "Generator",
    "Grid",
    "Line",
    "Inverter",
    "SlackGenerator",
    "SlackLine",
    "ThreeWindingTransformer",
    "Transformer",
    "RoutineEvaluation",
    "Secret",
    "Segment",
    "Server",
    "SetPoint",
    "String",
    "RoutineObject",
    "RoutineObjectInstance",
    "Tab",
    "Trace",
]
