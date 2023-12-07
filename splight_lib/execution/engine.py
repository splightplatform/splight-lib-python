from enum import Enum, auto
from typing import Set

import pytz
from apscheduler.events import EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from splight_lib.execution.task import BaseTask
from splight_lib.logging._internal import LogTags, get_splight_logger


class EngineStatus(Enum):
    RUNNING = auto()
    STOPPED = auto()
    FINISHED = auto()
    FAILED = auto()


class ExecutionEngine:
    def __init__(self):
        self._logger = get_splight_logger("ExecutionEngine")
        self._logger.info(
            "Execution client initialized.", tags=LogTags.RUNTIME
        )
        self._blocking_sch = BlockingScheduler(timezone=pytz.UTC)
        self._background_sch = BackgroundScheduler(
            timezone=pytz.UTC, daemon=True
        )
        self._critical_jobs: Set[str] = set()
        self._blocking_sch.add_listener(
            self._task_fail_callbak, EVENT_JOB_ERROR
        )
        self._background_sch.add_listener(
            self._task_fail_callbak, EVENT_JOB_ERROR
        )
        self._running = False
        self._state = EngineStatus.STOPPED

    @property
    def running(self) -> bool:
        return self._running

    @property
    def state(self) -> EngineStatus:
        return self._state

    def start(self):
        """Starts the the schedulers."""
        self._running = True
        self._state = EngineStatus.RUNNING
        if self._background_sch.get_jobs():
            self._background_sch.start()
        if self._blocking_sch.get_jobs():
            self._blocking_sch.start()
        self._logger.info("Execution Engine started", tags=LogTags.RUNTIME)

    def stop(self):
        """Stops all the schedulers and its task without waiting to finish."""
        if self._blocking_sch.running:
            self._blocking_sch.shutdown(wait=False)
        if self._background_sch.running:
            self._background_sch.shutdown(wait=False)
        self._running = False
        self._state = EngineStatus.STOPPED
        self._logger.info("Execution Engine stopped", tags=LogTags.RUNTIME)

    def add_task(
        self,
        task: BaseTask,
        in_background: bool = True,
        exit_on_fail: bool = False,
    ):
        """Adds new task to the corresponding scheduler.

        Parameters
        ----------
        task: BaseTask
            Instance of Task to be scheduled.
        in_background: bool
            Wheter to run the task using the BackgroundScheduler or the
            BlockingScheduler
        exit_on_fail: bool
            Used to stop the engine if the task execution failed. This
            parameter is usefull to declare critical tasks.
        """
        if in_background:
            job = self._background_sch.add_job(**task.as_job())
        else:
            job = self._blocking_sch.add_job(**task.as_job())
        if exit_on_fail:
            self._critical_jobs.add(job.id)
        self._logger.info(f"Job {job.id} added", tags=LogTags.RUNTIME)

    def _task_fail_callbak(self, event: JobExecutionEvent):
        if event.job_id in self._critical_jobs:
            self._logger.error(
                "An error ocurred in job execution. Stopping engine"
            )
            self.stop()
            self._state = EngineStatus.FAILED
