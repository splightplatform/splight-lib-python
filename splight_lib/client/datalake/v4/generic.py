from datetime import datetime
from enum import Enum
from typing import Optional, TypeAlias
from uuid import UUID

from pydantic import BaseModel

# NEW API GENERICS
TimeseriesId: TypeAlias = UUID
Timestamp: TypeAlias = datetime
Value: TypeAlias = float | bool | str | int
Cursor: TypeAlias = str


class AggregationFunction(str, Enum):
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"


class TimeUnit(str, Enum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class ValueType(str, Enum):
    FLOAT = "float"
    INT = "int"
    STRING = "string"
    BOOL = "bool"


class Settings(BaseModel):
    """Metadata fixed per timeseries."""

    value_type: ValueType


class DataPointWrite(BaseModel):
    idempotency_key: str
    timestamp: Timestamp
    value: Value


class DataPointRead(BaseModel):
    timestamp: Timestamp
    value: Value


class QueryResponse(BaseModel):
    """
    `data_points` are returned sorted by timestamp, according to 'sort' param passed to read().
    """

    data_points: list[DataPointRead]
    cursor: Optional[Cursor]


class Aggregate(BaseModel):
    window_start: Timestamp
    window_end: Timestamp
    value: Value


class TimeWindow(BaseModel):
    unit: TimeUnit = TimeUnit.SECOND
    size: int


# TRANSITION API GENERICS
class TransitionSchemaName(str, Enum):
    DEFAULT = "default"
    SOLUTIONS = "solutions"


class TransitionSort(int, Enum):
    ASC = 1
    DESC = -1


# class TransitionQueryResponse(PaginatedResponse[dict]):
#     pass
