import os
import sys
import time
from typing import Optional
from abc import ABCMeta, abstractmethod
from splight_lib.task import TaskManager
from splight_lib import logging
from tempfile import NamedTemporaryFile


class HealthCheckException(Exception):
    pass


class AbstractComponent(metaclass=ABCMeta):
    managed_class = None
    logger = logging.getLogger()
    healthcheck_interval = 5

    def __init__(self, instance_id: str, environment: Optional[str] = None):
        self.health_file = NamedTemporaryFile(prefix="healthy_")
        self.task_manager = TaskManager()
        self.instance_id = instance_id
        self.environment = environment
        self.object = self.managed_class.objects.get(id=instance_id)

    def mark_unhealthy(self):
        self.logger.debug(f"Healthcheck file removed: {self.health_file}")
        self.health_file.close()

    def pre_execution(self) -> None:
        pass

    @abstractmethod
    def main_task(self) -> None:
        pass

    def refresh_task(self) -> None:
        pass

    def server_task(self) -> None:
        pass

    def healthcheck(self) -> None:
        while True:
            if not self.task_manager.healthcheck():
                self.logger.debug("A task has failed")
                self.mark_unhealthy()
                sys.exit()
            time.sleep(self.healthcheck_interval)

    def execute(self) -> None:
        self.pre_execution()

        self.task_manager.start_thread(target=self.refresh_task)
        self.task_manager.start_thread(target=self.server_task)
        self.task_manager.start_thread(target=self.main_task)

        self.healthcheck()
