from abc import abstractmethod
import logging
import time
from typing import List, Optional, Type
from splight_models.connector import ClientConnector, ServerConnector
from splight_models.mapping import ClientMapping, ServerMapping
from splight_models import Variable
from splight_lib.execution import Thread
from .abstract import AbstractComponent


logger = logging.getLogger()


class AbstractIOComponent(AbstractComponent):
    mapping_class: Type = None
    mappings: List = []

    def __init__(self, *args, **kwargs):
        self.execution_client.start(Thread(target=self.refresh_mappings_forever))
        super(AbstractIOComponent, self).__init__(*args, **kwargs)

    def map_variable(self, variables: List[Variable]) -> List[Variable]:
        """
        Fill the asset_id and attribute_id from path
        """
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
        """
        Fill the path from asset_id and attribute_id
        """
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

    def refresh_mappings_forever(self) -> None:
        if self.mapping_class is None:
            logger.debug("No mapping class to refresh")
            return
        time_interval: int = 60
        while True:
            logger.debug("Updating mapping in connector")
            self.mappings = self.database_client.get(
                resource_type=self.mapping_class,
                connector_id=self.instance_id
            )
            logger.debug(f"Maps found {len(self.mappings)}")
            time.sleep(time_interval)


class AbstractClientComponent(AbstractIOComponent):
    managed_class = ClientConnector
    mapping_class = ClientMapping

    def __init__(self,
                 instance_id: str,
                 namespace: Optional[str] = 'default'):
        self.execution_client.start(Thread(target=self.sync_mappings_to_device))
        super(AbstractClientComponent, self).__init__(instance_id, namespace)

    @abstractmethod
    def handle_write(self, variables: List[Variable]) -> None:
        pass

    @abstractmethod
    def handle_subscribe(self, variables: List[Variable]) -> None:
        pass

    @abstractmethod
    def handle_unsubscribe(self, variables: List[Variable]):
        pass

    def sync_mappings_to_device(self):
        default_args = {"period": 5000}
        old_status = set()
        while True:
            new_status = set(self.mappings)
            if old_status != new_status:
                mappings_to_subscribe = new_status - old_status
                variables_to_subscribe = [
                    Variable(path=m.path, args=default_args)
                    for m in mappings_to_subscribe
                ]
                self.handle_subscribe(variables_to_subscribe)

                mappings_to_unsubscribe = old_status - new_status
                variables_to_unsubscribe = [
                    Variable(path=m.path, args=default_args)
                    for m in mappings_to_unsubscribe
                ]
                self.handle_unsubscribe(variables_to_unsubscribe)
            old_status = new_status
            time.sleep(10)


class AbstractServerComponent(AbstractIOComponent):
    managed_class = ServerConnector
    mapping_class = ServerMapping

    def __init__(self,
                 instance_id: str,
                 namespace: Optional[str] = 'default'):
        self.execution_client.start(Thread(target=self.sync_from_datalake))
        super(AbstractClientComponent, self).__init__(instance_id, namespace)

    @abstractmethod
    def handle_update(self, variables: List[Variable]) -> None:
        pass

    def sync_from_datalake(self):
        while True:
            logger.debug(f"Trying to fetch from datalake {len(variables)} variables")
            variables = [
                self.datalake_client.get(Variable, first=True, asset_id=mapping.asset_id, attribute_id=mapping.attribute_id)
                for mapping in self.mappings
            ]
            self.handle_update(variables)
            time.sleep(10)
