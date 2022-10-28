from splight_models import (
    Algorithm,
    Asset,
    Attribute,
    Connector,
    System,
    ClientMapping,
    Edge,
    Graph,
    Network,
    Notification,
    Node,
    MappingRule,
    ReferenceMapping,
    ServerMapping,
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
    Connector: {
        "path": "connector"
    },
    ClientMapping: {
        "path": "mapping/client-mapping"
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
    MappingRule: {
        "path": "rule"
    },
    ReferenceMapping: {
        "path": "mapping/reference-mapping"
    },
    ServerMapping: {
        "path": "mapping/server-mapping"
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
    System: {
        "path": "system"
    },
}
