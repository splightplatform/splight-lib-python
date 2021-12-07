import logging
from typing import Optional
from abc import ABCMeta, abstractmethod
from threading import Thread


class AbstractComponent(metaclass=ABCMeta):
    managed_class = None
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
        pass

    def execute(self, ) -> None:
        self.pre_execution()

        threads = [
            Thread(target=self.refresh_task),
            Thread(target=self.server_task),
            Thread(target=self.healthcheck_task),
        ]
        for thread in threads:
            thread.start()

        self.main_task()
