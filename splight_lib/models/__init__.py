from splight_lib.settings import SplightAPIVersion, api_settings

# Get API version
api_version = api_settings.API_VERSION

# Import only the models for the current version
if api_version == SplightAPIVersion.V3:
    from splight_lib.models._v3 import (
        DB_MODEL_TYPE_MAPPING,
        Action,
        AdvancedFilter,
        Alert,
        AlertItem,
        Asset,
        AssetKind,
        AssetParams,
        AssetRelationship,
        Attribute,
        Boolean,
        Bus,
        Chart,
        ChartItem,
        Component,
        ComponentObject,
        ComponentObjectInstance,
        ComponentType,
        CustomType,
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
        DataRequest,
        Endpoint,
        ExternalGrid,
        File,
        Filter,
        Function,
        FunctionItem,
        Generator,
        Grid,
        HubComponent,
        HubServer,
        InputParameter,
        Inverter,
        Line,
        Load,
        Metadata,
        Number,
        Output,
        Parameter,
        PipelineStep,
        PrivacyPolicy,
        QueryFilter,
        Routine,
        RoutineEvaluation,
        RoutineObject,
        RoutineObjectInstance,
        Secret,
        Segment,
        Server,
        SetPoint,
        SlackGenerator,
        SlackLine,
        SplightDatalakeBaseModel,
        String,
        Tab,
        Tag,
        ThreeWindingTransformer,
        Trace,
        Transformer,
    )

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
        "ChartItem",
        "Component",
        "ComponentObject",
        "ComponentObjectInstance",
        "ComponentType",
        "CustomType",
        "Endpoint",
        "Output",
        "InputParameter",
        "PrivacyPolicy",
        "Routine",
        "get_field_value",
        "Parameter",
        "DB_MODEL_TYPE_MAPPING",
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
        "SplightDatalakeBaseModel",
        "Bus",
        "ExternalGrid",
        "Generator",
        "Grid",
        "Line",
        "Load",
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
elif api_version == SplightAPIVersion.V4:
    from splight_lib.models._v4 import (
        DB_MODEL_TYPE_MAPPING,
        AdvancedFilter,
        Alert,
        AlertItem,
        Asset,
        AssetKind,
        AssetRelationship,
        Attribute,
        AttributeType,
        Boolean,
        Bus,
        Chart,
        ChartItem,
        Component,
        ComponentObject,
        ComponentObjectInstance,
        ComponentType,
        CustomType,
        Dashboard,
        DashboardAlertEventsChart,
        DashboardAlertListChart,
        DashboardAssetListChart,
        DashboardBarChart,
        DashboardBarGaugeChart,
        DashboardGaugeChart,
        DashboardHistogramChart,
        DashboardImageChart,
        DashboardStatChart,
        DashboardTableChart,
        DashboardTextChart,
        DashboardTimeseriesChart,
        DataRequest,
        Endpoint,
        ExternalGrid,
        File,
        Filter,
        Generator,
        Grid,
        HubComponent,
        HubServer,
        InputParameter,
        Line,
        Load,
        Metadata,
        Number,
        Output,
        Parameter,
        PipelineStep,
        PrivacyPolicy,
        ResourceSummary,
        Routine,
        RoutineEvaluation,
        RoutineObject,
        RoutineObjectInstance,
        Secret,
        Segment,
        Server,
        SlackLine,
        SplightDatalakeBaseModel,
        String,
        Tab,
        Tag,
        Trace,
        Transformer,
        ValueType,
        get_field_value,
    )

    __all__ = [
        "Alert",
        "AlertItem",
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
        "get_field_value",
        "Parameter",
        "DB_MODEL_TYPE_MAPPING",
        "AdvancedFilter",
        "SplightDatalakeBaseModel",
        "Chart",
        "ChartItem",
        "Dashboard",
        "DashboardAlertEventsChart",
        "DashboardAlertListChart",
        "DashboardAssetListChart",
        "DashboardBarChart",
        "DashboardBarGaugeChart",
        "DashboardGaugeChart",
        "DashboardHistogramChart",
        "DashboardImageChart",
        "DashboardStatChart",
        "DashboardTableChart",
        "DashboardTextChart",
        "DashboardTimeseriesChart",
        "Filter",
        "Tab",
        "DataRequest",
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
else:
    raise ImportError(f"No models available for API version: '{api_version}'.")
