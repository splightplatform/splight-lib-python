from datetime import datetime
from enum import Enum
from typing import TypeAlias

Timestamp: TypeAlias = datetime
Value: TypeAlias = float | bool | str | int


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


class TransitionSchemaName(str, Enum):
    DEFAULT = "default"
    SOLUTIONS = "solutions"


class TransitionSort(int, Enum):
    ASC = 1
    DESC = -1
