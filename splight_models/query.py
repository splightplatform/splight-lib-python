from enum import Enum
from typing import Dict, Union, List, Optional
from pydantic import validator, root_validator
from splight_models.base import SplightBaseModel

class QuerySource(str, Enum):
    ALGORITHM = "Algorithm"
    CONNECTOR = "Connector"

class Query(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    source: QuerySource
    component_id: str = None
    output_format: str
    target: str = None
    collection: str = None
    filters: Dict = {}
    limit: int = 10000
    skip: int = 0
    sort: Union[List, str] = ['timestamp__desc']
    add_fields: Union[List, str] = []
    group_id: Union[List, str] = []
    group_fields: Union[List, str] = []
    rename_fields: Union[List, str] = []
    project_fields: Union[List, str] = []
    timezone_offset: float = 0.0 # UTC
    query_params: str = None

    @root_validator(pre=True)
    def component_id_validate(cls, values):
        component_id = values.get("component_id")
        if component_id:
            return values
        source = values.get("source")
        if source == QuerySource.CONNECTOR:
            values["component_id"] = "default"
            return values
        raise ValueError(f"component_id is required when source is {QuerySource.ALGORITHM}")

    @validator("filters", always=True)
    def filters_validate(cls, filters, values):
        source = values.get("source")
        component_id = values.get("component_id")
        if source == QuerySource.CONNECTOR and component_id != "default":
            filters["instance_id"] = component_id
        return filters

    @validator("collection", always=True)
    def collection_validate(cls, collection, values):
        source = values.get("source")
        if source == QuerySource.ALGORITHM:
            return values.get("component_id")
        return "default"

    @validator("target", always=True)
    def target_validate(cls, target, values):
        source = values.get("source")
        if source == QuerySource.CONNECTOR:
            target = "value"
        if not target:
            raise ValueError("Target is required for algorithm outputs")
        return target

    @validator("query_params", always=True)
    def query_params_validate(cls, query_params, values):
        if query_params is None:
            query_params = f"?source={values['collection']}&"
            query_params += "&".join([f"{k}={','.join([str(i) for i in v])}" if type(v) == list else f"{k}={v}" for k, v in values["filters"].items()]) + "&" if values["filters"] else ""
            query_params_fields = ["limit", "skip", "sort"]
            underscored_fields = ["limit", "skip"]
            for k in query_params_fields:
                field = k if not k in underscored_fields else k + "_"
                if type(values[k]) == list:
                    query_params += f"{field}={','.join(values[k])}&"
                else:
                    query_params += f"{field}={values[k]}&"
            query_params = query_params[:-1]
        return query_params
