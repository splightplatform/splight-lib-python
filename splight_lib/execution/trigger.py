from datetime import datetime, tzinfo
from typing import Optional, Union

from apscheduler.triggers.interval import (
    IntervalTrigger as BaseIntervalTrigger,
)
from apscheduler.util import normalize


class IntervalTrigger(BaseIntervalTrigger):
    """Reimplementation of apscheduler InternalTrigger to run on start"""

    def __init__(
        self,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        start_date: Optional[Union[datetime, str]] = None,
        end_date: Optional[Union[datetime, str]] = None,
        timezone: Optional[Union[tzinfo, str]] = None,
        jitter: int = None,
        run_on_start: bool = True,
    ):
        super().__init__(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            start_date=start_date,
            end_date=end_date,
            timezone=timezone,
            jitter=jitter,
        )
        self._run_on_start = run_on_start

    def get_next_fire_time(self, previous_fire_time, now):
        if self._run_on_start:
            self._run_on_start = False
            return normalize(now)
        else:
            return super().get_next_fire_time(previous_fire_time, now)
