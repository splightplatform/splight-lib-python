from splight_lib.constants import ENGINE_PREFIX

MODEL_NAME_MAP = {
    "alert": f"{ENGINE_PREFIX}/alert/alerts/",
    "asset": f"{ENGINE_PREFIX}/assets/",
    "attribute": f"{ENGINE_PREFIX}/attributes/",
    "component": f"{ENGINE_PREFIX}/component/components/",
    "componentobject": f"{ENGINE_PREFIX}/component/objects/",
    "file": f"{ENGINE_PREFIX}/files/",
    "query": f"{ENGINE_PREFIX}/queries/",
    "secret": f"{ENGINE_PREFIX}/secrets/",
    "setpoint": f"{ENGINE_PREFIX}/setpoints/",
}

CUSTOM_PATHS_MAP = {
    "set-asset-attribute": "{prefix}/assets/{asset}/set-attribute/",
    "get-asset-attribute": "{prefix}/assets/{asset}/get-attribute/",
}
