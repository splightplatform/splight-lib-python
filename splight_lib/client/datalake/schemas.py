from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Iterator, List, Optional, TypeVar

from pydantic import BaseModel, Field


class TraceType(str, Enum):
    QUERY = "QUERY"
    EXPRESSION = "EXPRESSION"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


class Trace(BaseModel):
    ref_id: str
    type: Optional[TraceType] = None
    expression: Optional[dict] = None
    pipeline: Optional[List[dict]] = None

    class Config:
        use_enum_values = True


PipelineStep: TypeVar = Dict[str, str]
Pipeline: TypeVar = List[PipelineStep]
DataResponse: TypeVar = Iterator[Dict]


class DataRequest(BaseModel):
    collection: str = "default"
    sort_field: str = "timestamp"
    sort_direction: int = Field(-1, ge=-1, le=1)
    limit: int = Field(10000, ge=1, le=10000)
    # tzinfo: timezone = timezone.utc
    max_time_ms: int = Field(3000, ge=1, le=3000)
    from_timestamp: Optional[datetime] = None
    to_timestamp: Optional[datetime] = None
    traces: List[Trace]
    aggregation_query: Optional[Dict] = None

    class Config:
        arbitrary_types_allowed = True

    def dict(self):
        result = self.model_dump()
        for key, value in result.items():
            if isinstance(value, timezone):
                result[key] = str(value)
        return result


class DataRecords(BaseModel):
    collection: str
    records: List[Dict]
