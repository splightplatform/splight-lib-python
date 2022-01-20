import time
import logging
from typing import Optional, Tuple
from abc import ABCMeta, abstractmethod

from .abstract import AbstractComponent


logger = logging.getLogger()


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
            if str(mapping.path) == str(path):
                return mapping.asset.pk, mapping.attribute.name
        logger.debug(f"No mapping found for path {path}")
        return None

    def unmap_variable(self, asset_pk: int, field: str) -> Optional[str]:
        for mapping in self.mappings:
            if str(mapping.asset.pk) == str(asset_pk) and str(mapping.attribute.name) == str(field):
                return mapping.path
        logger.debug(f"No reverse mapping found for asset id {asset_pk}, field {field}")
        return None

    def refresh_task(self) -> None:
        time_interval: int = 60
        while True:
            logger.debug("Updating mapping in connector")
            self.mappings = list(self.mapping_model.objects.prefetch_related("asset").filter(connector_id=self.connector_id))
            logger.debug(f"Maps found {len(self.mappings)}")
            time.sleep(time_interval)
