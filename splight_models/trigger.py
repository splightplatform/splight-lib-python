from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional, Callable, List


class TriggerGroup(BaseModel):
    id: Optional[str]
    name: str


class Trigger(BaseModel):

    @staticmethod
    def renotify_time_checker(renotify_unit, renotify_time) -> bool:
        if renotify_unit != "minutes":
            renotify_time *= (
                (60 * (renotify_unit == "hours"))
                + (60 * 24 * (renotify_unit == "days"))
                + (60 * 24 * 7 * (renotify_unit == "weeks"))
            )
        if renotify_time < 1 or renotify_time > 60 * 24 * 365:
            return False
        return True

    class TriggerPriority(Enum):
        HIGH = "high"
        STANDARD = "standard"

    class Condition(Enum):
        GREATER = "gt"
        LOWER = "lt"
        LOWER_EQUAL = "lte"
        GREATER_EQUAL = "gte"
        EQUAL = "eq"
        NOT_EQUAL = "ne"

    class TimeUnit(Enum):
        MINUTES = "minutes"
        HOURS = "hours"
        DAYS = "days"
        WEEKS = "weeks"

    id: Optional[str]
    trigger_group_id: str
    asset_id: str
    attribute_id: str
    priority: str
    notification_message: str
    condition: str
    value: float
    renotify: bool
    renotify_unit: Optional[str]
    renotify_time: Optional[int]


    @validator('priority')
    def priority_validate(cls, v):
        priorities: List[str] = [item.value for item in cls.TriggerPriority]
        if v not in priorities:
            raise ValueError(f"Priority must be of of these: {priorities}")
        return v

    @validator('condition')
    def condition_validate(cls, v):
        conditions: List[str] = [item.value for item in cls.Condition]
        if v not in conditions:
            raise ValueError(f"Condition must be of of these: {conditions}")
        return v

    @validator('renotify_unit')
    def renotify_unit_validate(cls, v, values):
        renotify: bool = values['renotify']
        if renotify:
            if v not in [item.value for item in cls.TimeUnit]:
                raise ValueError("Renotify unit is required.")
        return v
    
    @validator('renotify_time')
    def renotify_time_validate(cls, v, values):
        renotify: bool = values['renotify']
        if renotify:
            if v is None:
                raise ValueError("Renotify time is required.")
            if not cls.renotify_time_checker(values['renotify_unit'], v):
                raise ValueError(f"Renotification time exceeds bounds. Min: 1 minute, Max: 1 year")
        return v

    @property
    def condition_is_valid(self) -> Callable[[float], bool]:
        EPS: float = 5e-2

        if self.condition == "gt":
            return lambda a: a > self.value if a is not None else False
        if self.condition == "lt":
            return lambda a: a < self.value if a is not None else False
        if self.condition == "lte":
            return lambda a: a <= self.value if a is not None else False
        if self.condition == "gte":
            return lambda a: a >= self.value if a is not None else False
        if self.condition == "eq":
            return lambda a: abs(a - self.value) < EPS if a is not None else False
        if self.condition == "ne":
            return lambda a: abs(a - self.value) > EPS if a is not None else False
