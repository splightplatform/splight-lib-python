from splight_lib.constants import ENGINE_PREFIX, HUB_PREFIX

MODEL_NAME_MAP = {
    "advancedfilter": f"{ENGINE_PREFIX}/alert/advancedfilters/",
    "alert": f"{ENGINE_PREFIX}/alert/alerts/",
    "asset": f"{ENGINE_PREFIX}/asset/assets/",
    "assetkind": f"{ENGINE_PREFIX}/asset/kinds/",
    # TODO: update to new endpoint for attributes
    "attribute": f"{ENGINE_PREFIX}/attributes/",
    "metadata": f"{ENGINE_PREFIX}/metadata/",
    "chart": f"{ENGINE_PREFIX}/dashboard/charts/",
    "chartitem": f"{ENGINE_PREFIX}/dashboard/chartitems/",
    "component": f"{ENGINE_PREFIX}/component/components/",
    "componentobject": f"{ENGINE_PREFIX}/component/objects/",
    "dashboard": f"{ENGINE_PREFIX}/dashboard/dashboards/",
    "file": f"{ENGINE_PREFIX}/files/",
    "filter": f"{ENGINE_PREFIX}/dashboard/filters/",
    "function": f"{ENGINE_PREFIX}/function/functions/",
    "query": f"{ENGINE_PREFIX}/queries/",
    "routineobject": f"{ENGINE_PREFIX}/component/routines/",
    "secret": f"{ENGINE_PREFIX}/secrets/",
    "setpoint": f"{ENGINE_PREFIX}/setpoints/",
    "solution": f"{ENGINE_PREFIX}/solution/solutions/",
    "tab": f"{ENGINE_PREFIX}/dashboard/tabs/",
    "hubsolution": f"{HUB_PREFIX}/solution/solutions/",
    "hubsolutionversion": f"{HUB_PREFIX}/solution/versions/",
}

CUSTOM_PATHS_MAP = {
    "set-asset-attribute": "{prefix}/assets/{asset}/set-attribute/",
    "get-asset-attribute": "{prefix}/assets/{asset}/get-attribute/",
    "decrypt-secret": "{prefix}/secrets/decrypt/",
}
