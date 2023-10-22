import sys
import threading
import time
import uuid
from functools import wraps
from subprocess import Popen as DefaultPopen
from threading import Event, Lock
from threading import Thread as DefaultThread
from typing import Any, Callable, List, Optional, Tuple, Union

from splight_lib.abstract.client import AbstractClient
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.models.component import ComponentStatus

logger = get_splight_logger()


class Empty(object):
    pass


class Task:
    """A periodic task for the scheduler."""

    def __init__(
        self,
        handler: Callable[[Any], None],
        args: Tuple,
        period: int,
        hash: str = None,
    ) -> None:
        if hash is None:
            hash = str(uuid.uuid4())
        self.hash = hash
        self.args = args
        self.period = period
        self.handler = handler
        self._name = self.handler

    def __repr__(self):
        return "<%s(%s)>" % (self.__class__.__name__, self._name)


class TaskSet:
    """Set of Tasks with the same hash but different or equal periods."""

    def __init__(self, task: Task) -> None:
        self.hash: str = task.hash
        self.args = task.args
        self.handler = task.handler
        self._periods: List[int] = [task.period]
        self.next_event = time.time()

    def update_event(self) -> None:
        """Set next_event of the TaskSet."""
        if len(self._periods) > 0:
            self.next_event += min(self._periods)
        else:
            # 2**16 is enough to wait and don't overflow.
            self.next_event = time.time() + 2**16

    def in_time(self, now: float) -> bool:
        """
        Check if the TaskSet is in time to execute.

        Args:
            now (int): The time now.
            return (bool): Return True if the TaskSet is in time.
        """
        return self.next_event <= now

    def add_period(self, period: float) -> bool:
        """
        Add new task period to the set. Update next event if is needed.

        Args:
            period (float): New scan period to add.
            return (bool): Return True if the task needs to
                be recalculated.
        """
        self._periods.append(period)

        # If is the first period, recalculate the next_event
        if len(self._periods) <= 1:
            self.next_event = time.time()
            return True

        return period == min(self._periods)

    def remove_period(self, period: float) -> bool:
        """
        Remove a task period to the list. Update execute if is needed.

        Args:
            period (float): Scan period to remove.
            return (bool): Return True if the next_event needs to
                be recalculated.
        """
        if period not in self._periods:
            return False

        # If is the min, you has to run the scheduler
        ret: bool = period == min(self._periods)

        # Precondition: period in self._periods
        self._periods.remove(period)

        return ret


class TaskMap:
    """
    Class used to manage tasks on the scheduler.
    """

    def __init__(self) -> None:
        self._map: dict[str, Task] = {}

    def add_task(self, task: Task) -> bool:
        """
        Add new task to the map.

        Args:
            task (Task): Task to add.
            return (bool): Return True if a scheduler run is needed.
        """
        if task.hash not in self._map:
            self._map[task.hash] = TaskSet(task)
            return True

        return self._map[task.hash].add_period(task.period)

    def remove_task(self, task: Task) -> bool:
        """
        Add new task to the map.

        Args:
            task (Task): Task to removed.
            return (bool): Return True if a scheduler run is needed.

        Note: The period is needed to prevent deleting other scan.
        """
        if task.hash not in self._map:
            return False

        # This don't delete the key if is empty, it does not bother
        return self._map[task.hash].remove_period(task.period)

    def get_list(self) -> List[TaskSet]:
        """Get the list of scans."""
        return list(self._map.values())


class Scheduler:
    def __init__(self, event: Event) -> None:
        # The _event attr is used for controling the scheduler loop meanwhile
        # the _tasks_event is used to notify the scheduler that a task should
        # be executed
        self._event = event
        self._tasks = TaskMap()
        self._tasks_event = Event()
        self._mutex = Lock()
        self._to_add: List[Task] = []
        self._to_remove: List[Task] = []

    def start(self) -> None:
        """Scheduler infinite loop."""
        while self._event.is_set():
            # Update the task list
            self._update_task_list()
            # Run the scheduler task
            near_event = self._schedule()
            # Get the next event
            next_event_time = near_event - time.time()

            # Wait until next event or someone trigger the event
            self._tasks_event.wait(timeout=next_event_time)
            self._tasks_event.clear()

    def stop(self) -> None:
        if self._event.is_set():
            self._event.clear()

    def _schedule(self) -> float:
        """Scheduler main task."""
        now = time.time()
        near_event: float = now + 65536  # 2**16

        for task_set in self._tasks.get_list():
            if task_set.in_time(now):
                task_set.handler(*task_set.args)
                task_set.update_event()

            near_event = min(near_event, task_set.next_event)

        return near_event

    def _notify_scheduler(self) -> None:
        """
        Unlock the scheduler if is locked.
        This will run the scheduler main task.
        """
        self._tasks_event.set()

    def schedule(self, task: Task) -> None:
        """
        Add new task to the scheduler.

        Args:
            task (Task): The new job.
        """

        with self._mutex:
            self._to_add.append(task)

        self._notify_scheduler()

    def unschedule(self, task: Task) -> None:
        """
        Delete a task from the scheduler.

        Args:
            task (Task): Job to delete.
        """
        with self._mutex:
            self._to_remove.append(task)

        self._notify_scheduler()

    def _update_task_list(self) -> None:
        """
        Update the task list.
        """
        with self._mutex:
            for task in self._to_add:
                self._tasks.add_task(task)
            for task in self._to_remove:
                self._tasks.remove_task(task)

            self._to_add = []
            self._to_remove = []


class Thread(DefaultThread):
    def __init__(self, target: Callable, args: Tuple = (), **kwargs) -> None:
        target = self.store_result(target)
        self.result = Empty()
        super().__init__(target=target, args=args, name=target, **kwargs)

    def store_result(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.result = func(*args, **kwargs)
            return self.result

        return wrapper

    def exit_ok(self) -> bool:
        return not isinstance(self.result, Empty)

    def kill(self) -> None:
        pass

    def terminate(self) -> None:
        pass


class Popen(DefaultPopen):
    def __init__(self, args: List[str]) -> None:
        self.args: List[str] = args
        super(Popen, self).__init__(args)

    def is_alive(self) -> bool:
        return self.poll() is None

    def exit_ok(self) -> bool:
        return self.poll() == 0


class ExecutionClient(AbstractClient):
    def __init__(self, *args, **kwargs):
        self._event = Event()
        self.processes: List[Popen] = []
        self.threads: List[Thread] = []

        self._register_exit_functions()
        super(ExecutionClient, self).__init__(*args, **kwargs)
        logger.info("Execution client initialized.", tags=LogTags.RUNTIME)
        self._exc = None
        self._thread_exc = None

    @property
    def event(self) -> Event:
        return self._event

    def _register_exit_functions(self) -> None:
        excepthook = sys.excepthook
        thread_exchook = threading.excepthook

        def wrap_excepthook(type, value, traceback):
            self._exc = (type, value, traceback)
            self.terminate_all()
            excepthook(type, value, traceback)

        def wrap_thread_excepthook(args):
            self._thread_exc = (
                args.exc_type,
                args.exc_value,
                args.exc_traceback,
            )
            self.terminate_all()
            thread_exchook(args)

        sys.excepthook = wrap_excepthook
        threading.excepthook = wrap_thread_excepthook

    def __del__(self) -> None:
        self.terminate_all()

    def terminate_all(self) -> None:
        # Set the event to False to stop all threads
        # This will also stop the scheduler
        self._event.clear()

        for p in self.processes:
            p.terminate()

    def start(self, job=Union[Popen, Thread, Task]):
        # Set the event in true so the threads can run
        if not self._event.is_set():
            self._event.set()
        logger.info("Executing new job.", tags=LogTags.RUNTIME)
        if isinstance(job, Popen):
            return self._start_process(job)
        if isinstance(job, Thread):
            return self._start_thread(job)
        if isinstance(job, Task):
            return self._start_task(job)

    def stop(self, job=Union[Popen, Thread, Task]):
        if isinstance(job, Popen):
            raise NotImplementedError
        if isinstance(job, Thread):
            raise NotImplementedError
        if isinstance(job, Task):
            return self._stop_task(job)

    def _start_process(self, job: Popen) -> None:
        logger.debug("Starting process", tags=LogTags.RUNTIME)
        self.processes.append(job)
        return

    def _start_thread(self, job: Thread) -> None:
        logger.debug("Starting Thread", tags=LogTags.RUNTIME)
        self.threads.append(job)
        job.start()
        return

    def _start_task(self, job: Task) -> None:
        logger.debug("Starting Task", tags=LogTags.RUNTIME)
        if not getattr(self, "_scheduler", None):
            # Instantiate and start Scheduler thread
            self._scheduler = Scheduler(self._event)
            self._start_thread(
                Thread(target=self._scheduler.start, daemon=False)
            )

        return self._scheduler.schedule(job)

    def _stop_task(self, job: Task) -> None:
        logger.debug("Stopping Task", tags=LogTags.RUNTIME)
        return self._scheduler.unschedule(job)

    def is_alive(self) -> bool:
        threads_status = [p.is_alive() for p in self.processes + self.threads]
        return all(threads_status)

    def healthcheck(self) -> Tuple[bool, ComponentStatus]:
        """Check if the component is alive and return the status.

        Returns
        -------
        Tuple[bool, ComponentStatus]
            Tuple with the first value being True if the component
            The second value is the status of the component.
        """
        alive = self.is_alive()
        if alive:
            status = ComponentStatus.RUNNING
        else:
            status = (
                ComponentStatus.FAILED
                if self.get_last_exception()
                else ComponentStatus.SUCCEEDED
            )
        return (alive, status)

    def get_last_exception(self) -> Optional[Exception]:
        """Get the last exception thrown in one of the threads.
        It assumes that there is only one thread that crashed
        It only works for the thread not the processes.
        """
        if self._exc:
            return self._exc[1]
        if self._thread_exc:
            return self._thread_exc[1]
        return None
