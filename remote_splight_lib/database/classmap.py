from splight_models import (
    Algorithm,
    Asset,
    Attribute,
    Connector,
    System,
    Mapping,
    Edge,
    Graph,
    Network,
    Notification,
    Node,
    Rule,
    Tag,
    BlockchainContract,
    BlockchainContractSubscription,
    Component,
    ComponentObject,
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
    Connector: {
        "path": "connector"
    },
    Mapping: {
        "path": "mapping"
    },
    Edge: {
        "path": "graph/edge"
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
        "path": "notification"
    },
    Node: {
        "path": "graph/node"
    },
    Rule: {
        "path": "rule"
    },
    Tag: {
        "path": "tag"
    },
    BlockchainContract: {
        "path": "blockchain/contract"
    },
    BlockchainContractSubscription: {
        "path": "blockchain/subscription"
    },
    System: {
        "path": "system"
    },
    Component: {
        "path": "components"
    },
    ComponentObject: {
        "path": "component-objects"
    }
}
