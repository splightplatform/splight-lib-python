from splight_models import (
    Asset,
    Attribute,
    File,
    Edge,
    Graph,
    Component,
    Notification,
    Query,
    Node,
    BlockchainContract,
    Component,
    ComponentObject,
    ComponentCommand,
    Secret,
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
    BlockchainContract: {
        "path": "blockchain/contract"
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
    Secret: {
        "path": "secret"
    },
}
