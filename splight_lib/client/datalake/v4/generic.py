from datetime import datetime
from enum import Enum
from typing import TypeAlias

Timestamp: TypeAlias = datetime
# Order in types is important. When parsing if float is first,
# bools will be interpreted as floats (1.0, 0.0) instead of bools.
Value: TypeAlias = bool | str | float


class AggregationFunction(str, Enum):
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    LAST = "last"


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
