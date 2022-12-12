from enum import Enum
from typing import Dict, Union, List, Optional
from pydantic import validator
# from splight_models import Boolean, String, Number
from splight_models.base import SplightBaseModel


class QuerySourceType(str, Enum):
    NATIVE = "Native"
    COMPONENT = "Component"


class Query(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    source_type: QuerySourceType
    source_component_id: Optional[str] = None
    source: str
    output_format: str
    target: str
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

    @validator("source", always=True)
    def source_validate(cls, source, values):
        source_type = values.get("source_type")
        native_sources = ["Boolean", "String", "Number"]
        if source_type == QuerySourceType.NATIVE and source not in native_sources:
            raise ValueError(f"source must be one of {native_sources} when source_type is {QuerySourceType.NATIVE}")
        return source

    @validator("target", always=True)
    def target_validate(cls, target, values):
        source_type = values.get("source_type")
        if source_type == QuerySourceType.NATIVE and target != "value":
            raise ValueError(f"target must be 'value' when source_type is {QuerySourceType.NATIVE}")
        if source_type == QuerySourceType.COMPONENT and not target:
            raise ValueError(f"target must be set when source_type is {QuerySourceType.COMPONENT}")
        return target

    @property
    def query_params(self):
        query_params = f"?source={self.source}&"
        query_params += "&".join([f"{k}={','.join([str(i) for i in v])}" if type(v) == list else f"{k}={v}" for k, v in self.filters.items()]) + "&" if self.filters else ""
        query_params_fields = ["limit", "skip", "sort"]
        underscored_fields = ["limit", "skip"]
        for k in query_params_fields:
            field = k if not k in underscored_fields else k + "_"
            if type(getattr(self, k)) == list:
                query_params += f"{field}={','.join(getattr(self, k))}&"
            else:
                query_params += f"{field}={getattr(self, k)}&"
        query_params = query_params[:-1]
        return query_params
