import logging
import os
import signal
import time
from typing import Optional
from abc import ABCMeta, abstractmethod
from threading import Thread


class HealthCheckException(Exception):
    pass



class AbstractComponent(metaclass=ABCMeta):
    managed_class = None
    healthcheck_key = None
    healthcheck_interval = 5
    logger = logging.getLogger()

    def __init__(self, instance_id: str, environment: Optional[str] = None):
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
        if self.healthcheck_key is None:
            return
        while True:
            if os.system(f"pgrep {self.healthcheck_key}  > /dev/null 2>&1") != 0:
                raise HealthCheckException(f"{self.healthcheck_key} process not alive")
            time.sleep(self.healthcheck_interval)

    def execute(self) -> None:
        self.pre_execution()

        threads = [
            Thread(target=self.refresh_task),
            Thread(target=self.server_task),
            Thread(target=self.main_task),
        ]
        for thread in threads:
            thread.start()

        try:
            self.healthcheck_task()
        except Exception as e:
            self.logger.exception(e)
            os.kill(os.getpid(), signal.SIGTERM)
