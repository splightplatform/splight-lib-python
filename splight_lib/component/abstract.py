import logging
import os
import signal
import time
from typing import Optional
from abc import ABCMeta, abstractmethod
from splight_lib.task import TaskManager


class HealthCheckException(Exception):
    pass


class AbstractComponent(metaclass=ABCMeta):
    managed_class = None
    healthcheck_interval = 5
    logger = logging.getLogger()

    def __init__(self, instance_id: str, environment: Optional[str] = None):
        self.task_manager = TaskManager()
        self.instance_id = instance_id
        self.environment = environment
        self.object = self.managed_class.objects.get(id=instance_id)

    def pre_execution(self) -> None:
        pass

    @abstractmethod
    def main_task(self) -> None:
        pass

    def refresh_task(self) -> None:
        pass

    def server_task(self) -> None:
        pass

    def healthcheck_task(self) -> None:
        while True:
            if not self.tasks_manager.all_tasks_ok():
                raise HealthCheckException(f"Some process is not running")

            time.sleep(self.healthcheck_interval)

    def execute(self) -> None:
        self.pre_execution()

        self.task_manager.start_thread(target=self.refresh_task)
        self.task_manager.start_thread(target=self.server_task)
        self.task_manager.start_thread(target=self.main_task)

        try:
            self.healthcheck_task()
        except Exception as e:
            self.logger.exception(e)
            os.kill(os.getpid(), signal.SIGTERM)
