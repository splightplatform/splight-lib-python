
import time
import atexit
import sys
import uuid
from typing import List, Callable, Union, Tuple, Any
from threading import (
    Thread as DefaultThread,
    Event,
    Lock,
)
from subprocess import Popen as DefaultPopen
from functools import wraps
from splight_abstract.client.abstract import AbstractClient
from splight_lib import logging


logger = logging.getLogger()


class Empty(object):
    pass


class Task:
    """A periodic task for the scheduler."""

    def __init__(self, handler: Callable[[Any], None], args: Tuple, period: int, hash: str = None) -> None:
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
            self.next_event = time.time() + 2 ** 16

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
    def __init__(self, *args, **kwargs) -> None:
        self._tasks = TaskMap()
        self._event = Event()
        self._mutex = Lock()
        self._to_add: List[Task] = []
        self._to_remove: List[Task] = []

    def start(self) -> None:
        """Scheduler infinite loop."""
        self._stop = False
        while not self._stop:
            # Update the task list
            self._update_task_list()
            # Run the scheduler task
            near_event = self._schedule()
            # Get the next event
            next_event_time = near_event - time.time()

            # Wait until next event or someone trigger the event
            self._event.wait(timeout=next_event_time)
            self._event.clear()

    def stop(self) -> None:
        self._stop = True

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
        self._event.set()

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
        self.processes: List[Thread] = []
        self.threads: List[Popen] = []

        self._register_exit_functions()
        super(ExecutionClient, self).__init__(*args, **kwargs)

    def _register_exit_functions(self) -> None:
        excepthook = sys.excepthook

        def wrap_excepthook(type, value, traceback):
            self.terminate_all()
            excepthook(type, value, traceback)

        atexit.register(self.terminate_all)
        sys.excepthook = wrap_excepthook

    def __del__(self) -> None:
        self.terminate_all()

    def terminate_all(self) -> None:
        for p in self.processes:
            p.terminate()

    def start(self, job=Union[Popen, Thread, Task]):
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
        logger.debug(f"Starting process {job}")
        self.processes.append(job)
        return

    def _start_thread(self, job: Thread) -> None:
        logger.debug(f"Starting Thread {job}")
        self.threads.append(job)
        job.start()
        return

    def _start_task(self, job: Task) -> None:
        logger.debug(f"Starting Task {job}")
        if not getattr(self, '_scheduler', None):
            # Instantiate and start Scheduler thread
            self._scheduler = Scheduler()
            self._start_thread(Thread(target=self._scheduler.start))

        return self._scheduler.schedule(job)

    def _stop_task(self, job: Task) -> None:
        logger.debug(f"Stopping Task {job}")
        return self._scheduler.unschedule(job)

    def healthcheck(self):
        return all([p.is_alive() or p.exit_ok() for p in self.processes + self.threads])
