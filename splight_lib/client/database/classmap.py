from splight_models import (
    Alert,
    AlertCondition,
    Asset,
    Attribute,
    File,
    Component,
    Notification,
    Query,
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
    File: {
        "path": "v2/engine/files"
    },
    Notification: {
        "path": "v2/account/notifications"
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
