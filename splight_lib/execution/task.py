from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional, Tuple

import pytz
from apscheduler.triggers.cron import CronTrigger

from splight_lib.execution.scheduling import Crontab, TaskPeriod
from splight_lib.execution.trigger import IntervalTrigger


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
    def __init__(
        self,
        target: Callable,
        crontab: Crontab,
        target_args: Optional[Tuple] = None,
    ):
        self._target = target
        self._trigger = CronTrigger(
            **crontab.model_dump(exclude_none=True), timezone=pytz.UTC
        )
        self._args = target_args

    @classmethod
    def from_cron_string(
        cls,
        target: Callable,
        cron_str: str,
        target_args: Optional[Tuple] = None,
    ):
        crontab = Crontab.from_string(cron_str)
        return cls(target, crontab, target_args)

    def as_job(self) -> dict:
        job_dict = {
            "func": self._target,
            "trigger": self._trigger,
        }

        if self._args:
            job_dict.update({"args": self._args})

        return job_dict
