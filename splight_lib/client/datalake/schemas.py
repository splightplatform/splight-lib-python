from datetime import datetime
from enum import Enum
from typing import Dict, Iterator, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class TraceType(str, Enum):
    QUERY = "QUERY"
    EXPRESSION = "EXPRESSION"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


class Trace(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    ref_id: str
    type: Optional[TraceType] = None
    expression: Optional[dict] = None
    pipeline: Optional[List[dict]] = None


PipelineStep: TypeVar = Dict[str, str]
Pipeline: TypeVar = List[PipelineStep]
DataResponse: TypeVar = Iterator[Dict]


class DataRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    collection: str = "default"
    sort_field: str = "timestamp"
    sort_direction: int = Field(-1, ge=-1, le=1)
    limit: int = Field(10000, ge=1, le=10000)
    # tzinfo: timezone = timezone.utc
    max_time_ms: int = Field(10000, ge=1, le=10000)
    from_timestamp: Optional[datetime] = None
    to_timestamp: Optional[datetime] = None
    traces: List[Trace]
    aggregation_query: Optional[Dict] = None

    def dict(self):
        result = self.model_dump()
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        return result


class DataRecords(BaseModel):
    collection: str
    records: List[Dict]
