from enum import auto
from typing import Set, Tuple

import pytz
from apscheduler.events import EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from strenum import PascalCaseStrEnum

from splight_lib.execution.task import BaseTask
from splight_lib.logging._internal import LogTags, get_splight_logger


class EngineStatus(PascalCaseStrEnum):
    RUNNING = auto()
    STOPPED = auto()
    FINISHED = auto()
    FAILED = auto()
    INITIALIZED = auto()
    UNKNOWN = auto()


class ExecutionEngine:
    def __init__(self):
        self._logger = get_splight_logger("ExecutionEngine")
        self._logger.info(
            "Execution client initialized.", tags=LogTags.RUNTIME
        )
        self._blocking_sch = BlockingScheduler(
            job_defaults={"misfire_grace_time": None},
            timezone=pytz.UTC,
        )
        self._background_sch = BackgroundScheduler(
            job_defaults={"misfire_grace_time": None},
            timezone=pytz.UTC,
            daemon=True,
        )
        self._critical_jobs: Set[str] = set()
        self._blocking_sch.add_listener(
            self._task_fail_callback, EVENT_JOB_ERROR
        )
        self._background_sch.add_listener(
            self._task_fail_callback, EVENT_JOB_ERROR
        )
        self._running = True
        self._state = EngineStatus.UNKNOWN

    @property
    def running(self) -> bool:
        return self._running

    @property
    def state(self) -> EngineStatus:
        return self._state

    def healthcheck(self) -> Tuple[bool, str]:
        return (self._running, self._state.value)

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
        max_instances: int = 1,
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
        max_instances: int = 1
            Maximum number of concurrently running instances allowed for this
            job
        """
        if in_background:
            job = self._background_sch.add_job(
                **task.as_job(), max_instances=max_instances
            )
        else:
            job = self._blocking_sch.add_job(
                **task.as_job(), max_instances=max_instances
            )
        if exit_on_fail:
            self._critical_jobs.add(job.id)
        self._logger.info(f"Job {job.id} added", tags=LogTags.RUNTIME)

    def _task_fail_callback(self, event: JobExecutionEvent):
        if event.job_id in self._critical_jobs:
            self._logger.error(
                "An error ocurred in job execution. Stopping engine"
            )
            self.stop()
            self._state = EngineStatus.FAILED
