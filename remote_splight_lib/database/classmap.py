from splight_models import (
    Asset,
    Attribute,
    File,
    Mapping,
    Edge,
    Graph,
    Component,
    Notification,
    Query,
    Node,
    Tag,
    BlockchainContract,
    BlockchainContractSubscription,
    Component,
    ComponentObject,
    ComponentCommand,
)


CLASSMAP = {
    Component: {
        "path": "component"
    },
    Asset: {
        "path": "asset"
    },
    Attribute: {
        "path": "attribute"
    },
    Mapping: {
        "path": "mapping"
    },
    Edge: {
        "path": "graph/edge"
    },
    File: {
        "path": "file"
    },
    Graph: {
        "path": "graph/graph"
    },
    # Namespace: {
    #     "path": "asset"
    # },
    Notification: {
        "path": "notification"
    },
    Node: {
        "path": "graph/node"
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
    Component: {
        "path": "components"
    },
    ComponentObject: {
        "path": "component-objects"
    },
    ComponentCommand: {
        "path": "component-commands"
    },
    Query: {
        "path": "query"
    },
}
