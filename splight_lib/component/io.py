import time
import logging
from typing import Optional, Tuple, List
from abc import ABCMeta, abstractmethod
from .abstract import AbstractComponent
from splight_models import Variable

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
    database = None
    datalake = None
    mappings = []
    mapping_model = None
    connector_id = None

    def map_variable(self, variables: List[Variable]) -> List[Variable]:
        result: List[Variable] = []
        for var in variables:
            mapping = list(filter(lambda x: x.path == var.path, self.mappings))

            if len(mapping) == 0:
                logger.debug(f"No mapping found for variable {var.json()}")
                continue

            var.asset_id = mapping[0].asset_id
            var.attribute_id = mapping[0].attribute_id
            result.append(var)
        return result

    def unmap_variable(self, variables: List[Variable]) -> List[Variable]:
        result: List[Variable] = []
        for var in variables:
            mapping = list(filter(lambda x: x.asset_id == var.asset_id and
                                  x.attribute_id == var.attribute_id, self.mappings))

            if len(mapping) == 0:
                logger.debug(f"No reverse mapping found for variable {var.json()}")
                continue

            var.path = mapping[0].path
            result.append(var)
        return result

    def refresh_task(self) -> None:
        time_interval: int = 60
        while True:
            logger.debug("Updating mapping in connector")
            self.mappings = self.database.get(resource_type = self.mapping_model, connector_id=self.connector_id)
            logger.debug(f"Maps found {len(self.mappings)}")
            time.sleep(time_interval)
