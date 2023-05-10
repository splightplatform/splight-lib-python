from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import validator

from splight_lib.models.base import SplightDatabaseBaseModel


class QuerySourceType(str, Enum):
    NATIVE = "Native"
    COMPONENT = "Component"


class Query(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    source_type: QuerySourceType
    source_component_id: Optional[str] = None
    output_format: str
    target: str
    filters: Dict = {}
    limit: int = 10000
    skip: int = 0
    sort: Union[List, str] = ["timestamp__desc"]
    add_fields: Union[List, str] = []
    group_id: Union[List, str] = []
    group_fields: Union[List, str] = []
    rename_fields: Union[List, str] = []
    project_fields: Union[List, str] = []
    timezone_offset: float = 0.0  # UTC

    @validator("source_component_id", always=True)
    def source_component_id_validate(cls, source_component_id, values):
        source_type = values.get("source_type")
        if (
            source_type == QuerySourceType.COMPONENT
            and not source_component_id
        ):
            raise ValueError(
                f"source must be set when source_type is {source_type}"
            )
        return source_component_id

    @validator("target", always=True)
    def target_validate(cls, target, values):
        source_type = values.get("source_type")
        if source_type == QuerySourceType.NATIVE and target != "value":
            raise ValueError(
                f"target must be 'value' when source_type is {source_type}"
            )
        if source_type == QuerySourceType.COMPONENT and not target:
            raise ValueError(
                f"target must be set when source_type is {source_type}"
            )
        return target

    @property
    def source(self):
        return (
            "default"
            if self.source_type == QuerySourceType.NATIVE
            else self.source_component_id
        )

    @property
    def query_params(self):
        query_params = f"?source={self.source}"
        if self.filters:
            joined_filters = "&".join(
                [
                    f"{k}={','.join([str(i) for i in v])}"
                    if type(v) == list
                    else f"{k}={v}"
                    for k, v in self.filters.items()
                ]
            )
            query_params += f"&{joined_filters}"
        if self.output_format:
            query_params += f"&output_format={self.output_format}"
        query_params_fields = ["limit", "skip", "sort"]
        underscored_fields = ["limit", "skip"]
        for k in query_params_fields:
            field = k if k not in underscored_fields else k + "_"
            if type(getattr(self, k)) == list:
                query_params += f"&{field}={','.join(getattr(self, k))}"
            else:
                query_params += f"&{field}={getattr(self, k)}"
        return query_params
