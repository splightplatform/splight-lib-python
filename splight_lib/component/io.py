# TODO simplify this class
from abc import abstractmethod
from typing import List, Type, Dict
from splight_models import (
    Connector,
    Mapping,
    Variable,
    Number,
    String,
    Boolean,
    MappingCreateEvent,
    MappingDeleteEvent,
)
from splight_lib import logging
from splight_lib.execution import Task
from splight_lib.component.abstract import AbstractComponent
from splight_models.communication.events import EventNames


logger = logging.getLogger()


class AbstractIOComponent(AbstractComponent):
    managed_class = Connector
    mapping_class: Type = None
    mappings: List = []
    _hashed_mappings: Dict = {}
    _hashed_mappings_by_path: Dict = {}

    def __init__(self, *args, **kwargs):
        super(AbstractIOComponent, self).__init__(*args, **kwargs)
        self.collection_name = 'default'
        self._retrieve_mappings()
        self._bind_mapping_events()

    def _load_instance_data(self):
        self.collection_name = 'default'
        self.communication_client_kwargs['instance_id'] = self.instance_id

    def _load_hooks(self):
        super()._load_hooks()
        self.datalake_client.add_pre_hook('save', self.hook_map_variable)

    def hook_map_variable(self, *args, **kwargs):
        """
        Hook to add info about asset_id attribute_id for variables
        """
        instances = kwargs.get("instances", [])
        for instance in instances:
            if not isinstance(instance, Variable):
                continue
            mapping = self._hashed_mappings_by_path.get(f"{instance.path}", None)
            if mapping is not None:
                instance.asset_id = mapping.asset_id
                instance.attribute_id = mapping.attribute_id
        if instances:
            kwargs['instances'] = instances
        return args, kwargs

    def map_variable(self, variables: List[Variable]) -> List[Variable]:
        """
        Fill the asset_id and attribute_id from path
        """
        result: List[Variable] = []
        for var in variables:
            mapping = self._hashed_mappings_by_path.get(var.path, None)
            if mapping is None:
                logger.debug(f"No mapping found for variable {var.json()}")
                continue

            var.asset_id = mapping.asset_id
            var.attribute_id = mapping.attribute_id
            result.append(var)
        return result

    def unmap_variable(self, variables: List[Variable]) -> List[Variable]:
        """
        Fill the path from asset_id and attribute_id
        """
        result: List[Variable] = []
        for var in variables:
            mapping = self._hashed_mappings.get(f"{var.asset_id}-{var.attribute_id}", None)
            if mapping is None:
                logger.debug(f"No reverse mapping found for variable {var.json()}")
                continue

            var.path = mapping.path
            result.append(var)
        return result

    def _retrieve_mappings(self):
        if self.mapping_class is None:
            logger.debug("No mapping class to refresh")
            return
        logger.debug("Retrieving mappings in connector")
        self.mappings = self.database_client.get(
            resource_type=self.mapping_class,
            connector_id=self.instance_id
        )
        self._hashed_mappings = {
            f"{m.asset_id}-{m.attribute_id}": m
            for m in self.mappings
        }
        self._hashed_mappings_by_path = {
            f"{m.path}": m
            for m in self.mappings
        }
        logger.debug(f"Maps found {len(self.mappings)}")
        logger.debug(self.mappings)

    def _bind_mapping_events(self):
        self.communication_client.bind(EventNames.MAPPING_CREATE, self._handle_mapping_created)
        self.communication_client.bind(EventNames.MAPPING_DELETE, self._handle_mapping_deleted)

    def _handle_mapping_created(self, data: str):
        if self.mapping_class is None:
            logger.debug("No mapping class to refresh")
            return
        logger.debug("Created mapping in connector")
        mapping = MappingCreateEvent.parse_raw(data).data
        self.mappings.append(mapping)
        self._hashed_mappings[f"{mapping.asset_id}-{mapping.attribute_id}"] = mapping
        self._hashed_mappings_by_path[f"{mapping.path}"] = mapping
        logger.debug(f"New mapping registered: {mapping}")
        logger.debug(f"Total mappings: {len(self.mappings)}")

    def _handle_mapping_deleted(self, data: str):
        if self.mapping_class is None:
            logger.debug("No mapping class to refresh")
            return
        mapping = MappingDeleteEvent.parse_raw(data).data
        self.mappings = [m for m in self.mappings if m.id != mapping.id]
        self._hashed_mappings.pop(f"{mapping.asset_id}-{mapping.attribute_id}", None)
        self._hashed_mappings_by_path.pop(f"{mapping.path}", None)
        logger.debug(f"Mapping deleted registered: {mapping}")
        logger.debug(f"Total mappings: {len(self.mappings)}")


class AbstractClientComponent(AbstractIOComponent):
    mapping_class = Mapping

    def __init__(self, *args, **kwargs):
        super(AbstractClientComponent, self).__init__(*args, **kwargs)
        self.type_to_output = {
            float: Number,
            int: Number,
            str: String,
            bool: Boolean,
        }
        self._mappings_last_sync = set()
        self.execution_client.start(Task(handler=self.sync_mappings_to_device, args=tuple(), period=10))

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
        new_status = set(self.mappings)
        if self._mappings_last_sync != new_status:
            mappings_to_subscribe = new_status - self._mappings_last_sync
            variables_to_subscribe = [
                Variable(
                    path=m.path,
                    args={"period": m.period},
                    asset_id=m.asset_id,
                    attribute_id=m.attribute_id)
                for m in mappings_to_subscribe
            ]
            try:
                self.handle_subscribe(variables_to_subscribe)
            except Exception as e:
                logger.exception(e)
                logger.error("Not possible to handle_subscribe. Will retry later")
                return

            mappings_to_unsubscribe = self._mappings_last_sync - new_status
            variables_to_unsubscribe = [
                Variable(
                    path=m.path,
                    args={"period": m.period},
                    asset_id=m.asset_id,
                    attribute_id=m.attribute_id)
                for m in mappings_to_unsubscribe
            ]
            try:
                self.handle_unsubscribe(variables_to_unsubscribe)
            except Exception as e:
                logger.exception(e)
                logger.error("Not possible to handle_subscribe. Will retry later")
                return
        self._mappings_last_sync = new_status
