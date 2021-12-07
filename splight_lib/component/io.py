import time
from typing import Optional, Tuple
from abc import ABCMeta, abstractmethod

from .abstract import AbstractComponent


class AbstractMasterSlave(metaclass=ABCMeta):
    @abstractmethod
    def send(self, data: dict) -> None:
        pass

    @abstractmethod
    def receive(self) -> dict:
        pass


class AbstractIOComponent(AbstractComponent):

    master: Optional[AbstractMasterSlave] = None
    slave: Optional[AbstractMasterSlave] = None
    datalake = None
    mappings = []
    mapping_model = None
    connector_id = None

    def map_variable(self, path: str) -> Optional[Tuple[int, str]]:
        for mapping in self.mappings:
            if mapping.path == path:
                return mapping.asset.pk, mapping.field
        return None

    def unmap_variable(self, asset_pk: int, field: str) -> Optional[str]:
        for mapping in self.mappings:
            if mapping.asset.pk == asset_pk and mapping.field == field:
                return mapping.path
        return None

    def refresh_task(self) -> None:
        # Update self.mappings whith the latest data from the static database
        while True:
            time_interval: int = 60
            self.mappings = list(self.mapping_model.objects.prefetch_related("asset").filter(connector_id=self.connector_id))
            time.sleep(time_interval)
