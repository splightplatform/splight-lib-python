from pydantic import Field
from enum import Enum
from typing import Dict, Optional, Union, List
from pydantic import validator, root_validator
from datetime import datetime, timezone
from splight_models.base import SplightBaseModel

class DatalakeModel(SplightBaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        validate_assignment = True


class ComponentDatalakeModel(DatalakeModel):
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        return {
            k: v['id'] if isinstance(v, dict) else v
            for k, v in d.items()
        }

class DatalakeOutputSource(str, Enum):
    ALGORITHM = "Algorithm"
    CONNECTOR = "Connector"

class DatalakeOutputQuery(SplightBaseModel):
    source: DatalakeOutputSource
    component_id: str = None
    output_format: str
    target: str = None
    collection: str = None
    filters: Dict = {}
    limit_: int = 10000
    skip_: int = 0
    sort: Union[List, str] = ['timestamp__desc']
    timezone_offset: float = 0.0 # UTC
    query_params: str = None

    @root_validator(pre=True)
    def component_id_validate(cls, values):
        component_id = values.get("component_id")
        if component_id:
            return values
        source = values.get("source")
        if source == DatalakeOutputSource.CONNECTOR:
            values["component_id"] = "default"
            return values
        raise ValueError(f"component_id is required when source is {DatalakeOutputSource.ALGORITHM}")

    @validator("filters", always=True)
    def filters_validate(cls, filters, values):
        source = values.get("source")
        component_id = values.get("component_id")
        if source == DatalakeOutputSource.CONNECTOR and component_id != "default":
            filters["instance_id"] = component_id
        return filters

    @validator("collection", always=True)
    def collection_validate(cls, collection, values):
        source = values.get("source")
        if source == DatalakeOutputSource.ALGORITHM:
            return values.get("component_id")
        return "default"

    @validator("target", always=True)
    def target_validate(cls, target, values):
        source = values.get("source")
        if source == DatalakeOutputSource.CONNECTOR:
            target = "value"
        if not target:
            raise ValueError("Target is required for algorithm outputs")
        return target

    @validator("query_params", always=True)
    def query_params_validate(cls, query_params, values):
        if query_params is None:
            query_params = f"?source={values['collection']}&"
            query_params += "&".join([f"{k}={','.join([str(i) for i in v])}" if type(v) == list else f"{k}={v}" for k, v in values["filters"].items()]) + "&" if values["filters"] else ""
            query_params_fields = ["limit_", "skip_", "sort"]
            for k in query_params_fields:
                if type(values[k]) == list:
                    query_params += f"{k}={','.join(values[k])}&"
                else:
                    query_params += f"{k}={values[k]}&"
            query_params = query_params[:-1]
        return query_params
