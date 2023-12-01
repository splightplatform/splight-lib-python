from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Callable, Dict, Optional, Tuple

import pytz
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pydantic import BaseModel


class TaskPeriod(BaseModel):
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    start_date: datetime = datetime.now(timezone.utc)
    end_date: Optional[datetime] = None


class BaseTask(ABC):
    @abstractmethod
    def as_job(self) -> Dict:
        ...


class PeriodicTask(BaseTask):
    def __init__(
        self,
        target: Callable,
        period: TaskPeriod,
        target_args: Optional[Tuple] = None,
    ):
        self._target = target
        self._args = target_args
        self._trigger = IntervalTrigger(
            **period.model_dump(), timezone=pytz.UTC
        )

    def as_job(self) -> dict:
        job_dict = {
            "func": self._target,
            "trigger": self._trigger,
        }

        if self._args:
            job_dict.update({"args": self._args})

        return job_dict


Task = PeriodicTask


class CronnedTask(BaseTask):
    _TRIGGER = "cron"

    def __init__(
        self, target: Callable, cron: str, target_args: Optional[Tuple] = None
    ):
        self._target = target
        self._cron = cron
        self._
        self._args = target_args

    def as_job(self) -> dict:
        return {
            "func": self._target,
            "trigger": self._TRIGGER,
            "cron": self._cron,
        }
