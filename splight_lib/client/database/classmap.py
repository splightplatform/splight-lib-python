from splight_models import (
    Alert,
    AlertCondition,
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
    HubComponent,
    ComponentObject,
    ComponentCommand,
    Secret,
    SetPoint,
)


CLASSMAP = {
    Component: {
        "path": "v2/engine/component/components"
    },
    Alert: {
        "path": "v2/engine/alert/alerts"
    },
    AlertCondition: {
        "path": "v2/engine/alert/conditions"
    },
    Asset: {
        "path": "v2/engine/assets"
    },
    Attribute: {
        "path": "v2/engine/attributes"
    },
    Edge: {
        "path": "v2/engine/graph/edges"
    },
    File: {
        "path": "v2/engine/files"
    },
    Graph: {
        "path": "v2/engine/graph/graphs"
    },
    Notification: {
        "path": "v2/account/notifications"
    },
    Node: {
        "path": "v2/engine/graph/nodes"
    },
    BlockchainContract: {
        "path": "v2/backoffice/blockchain/contracts"
    },
    ComponentObject: {
        "path": "v2/engine/component/objects"
    },
    ComponentCommand: {
        "path": "v2/engine/component/commands"
    },
    Query: {
        "path": "v2/engine/queries"
    },
    Secret: {
        "path": "v2/engine/secrets"
    },
    HubComponent: {
        "path": "v2/engine/hub/component-versions"
    },
    SetPoint: {
        "path": "v2/engine/setpoints"
    },
}
