from datetime import datetime, timezone
from typing import Optional, Union

from pydantic import (
    BaseModel,
    ValidationInfo,
    field_validator,
    model_serializer,
)

from splight_lib.execution.exceptions import InvalidCronString

FIELD_RANGE = {
    "month": (1, 12),
    "day": (1, 31),
    "week": (1, 53),
    "day_of_week": (0, 6),
    "hour": (0, 23),
    "minute": (0, 59),
    "second": (0, 59),
}


def validate_value_in_range(
    value: Union[int, str], min_value: int, max_value: int, name: str
):
    if isinstance(value, str):
        if "*" in value:
            return value
        elif value.isdigit():
            value = int(value)
            if not min_value <= value <= max_value:
                raise ValueError(
                    f"{name}'s value must be in range {min_value}-{max_value}"
                )
    elif isinstance(value, int):
        if not min_value <= value <= max_value:
            raise ValueError(
                f"{name}'s Value must be in range {min_value}-{max_value}"
            )
    return value


class TaskPeriod(BaseModel):
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    start_date: datetime = datetime.now(timezone.utc)
    end_date: Optional[datetime] = None


class Crontab(BaseModel):
    year: Optional[Union[str, int]] = None
    month: Optional[Union[str, int]] = None
    day: Optional[Union[str, int]] = None
    week: Optional[Union[str, int]] = None
    day_of_week: Optional[Union[str, int]] = None
    hour: Optional[Union[str, int]] = None
    minute: Optional[Union[str, int]] = None
    second: Optional[Union[str, int]] = None

    @field_validator(
        "month", "day", "week", "day_of_week", "hour", "minute", "second"
    )
    def validate_minute(cls, value: str, info: ValidationInfo):
        min_value, max_value = FIELD_RANGE[info.field_name]
        return validate_value_in_range(
            value, min_value, max_value, info.field_name
        )

    @classmethod
    def from_string(cls, cron_str: str) -> "Crontab":
        """Converts a crontab string into a Crontab instance.
        Since crontab by default uses 5 fields, seconds and years are set to
        None

        Parameters
        ----------
        cron_str : str
            The crontab string to convert

        Returns
        -------
        Crontab instance
        """
        elements = cron_str.split(" ")
        if len(elements) != 5:
            raise InvalidCronString(cron_str)
        return cls(
            minute=elements[0],
            hour=elements[1],
            day=elements[2],
            month=elements[3],
            day_of_week=elements[4],
        )

    @model_serializer
    def custom_serializer(self) -> str:
        """Serializes Crontab as a string.

        Returns
        -------
        str
            The crontab string.
        """
        return f"{self.minute} {self.hour} {self.day} {self.month} {self.day_of_week}"
