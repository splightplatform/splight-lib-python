from splight_models import (
    Algorithm,
    Asset,
    Attribute,
    BillingSettings,
    MonthBilling,
    Billing,
    DeploymentBillingItem,
    Chart,
    ChartItem,
    Connector,
    ClientMapping,
    Dashboard,
    Edge,
    Filter,
    Graph,
    Namespace,
    Network,
    Notification,
    Node,
    MappingRule,
    ReferenceMapping,
    ServerMapping,
    Tab,
    Tag,
    ValueMapping,
    BlockchainContract,
    BlockchainContractSubscription,
)


CLASSMAP = {
    Algorithm: {
        "path": "algorithm"
    },
    Asset: {
        "path": "asset"
    },
    Attribute: {
        "path": "attribute"
    },
    BillingSettings: {
        "path": "setup/billing-settings"
    },
    # MonthBilling: {
    #     "path": "asset"
    # },
    Billing: {
        "path": "billing"
    },
    # DeploymentBillingItem: {
    #     "path": "asset"
    # },
    Chart: {
        "path": "dashboard/chart"
    },
    ChartItem: {
        "path": "dashboard/chartitem"
    },
    Connector: {
        "path": "connector"
    },
    ClientMapping: {
        "path": "mapping/client-mapping"
    },
    Dashboard: {
        "path": "dashboard/dashboard"
    },
    Edge: {
        "path": "graph/edge"
    },
    Filter: {
        "path": "dashboard/filter"
    },
    Graph: {
        "path": "graph/graph"
    },
    # Namespace: {
    #     "path": "asset"
    # },
    Network: {
        "path": "network"
    },
    Notification: {
        "path": "asset"
    },
    Node: {
        "path": "graph/node"
    },
    MappingRule: {
        "path": "rule"
    },
    ReferenceMapping: {
        "path": "mapping/reference-mapping"
    },
    ServerMapping: {
        "path": "mapping/server-mapping"
    },
    Tab: {
        "path": "dashboard/tab"
    },
    Tag: {
        "path": "tag"
    },
    ValueMapping: {
        "path": "mapping/value-mapping"
    },
    BlockchainContract: {
        "path": "blockchain/contract"
    },
    BlockchainContractSubscription: {
        "path": "blockchain/subscription"
    },
}
