# TODO simplify this class
from abc import abstractmethod
from typing import List, Type, Dict
from splight_models import (
    Connector,
    ClientMapping,
    Variable,
    MappingRule,
    Notification,
    FloatValue,
    StrValue,
    BoolValue
)
from splight_lib import logging
from splight_lib.execution import Task
from splight_lib.component.abstract import AbstractComponent


logger = logging.getLogger()


class AbstractIOComponent(AbstractComponent):
    managed_class = Connector
    mapping_class: Type = None
    mappings: List = []
    rules: List = []
    _hashed_mappings: Dict = {}
    _hashed_mappings_by_path: Dict = {}
    _hashed_rules: Dict = {}

    def __init__(self, *args, **kwargs):
        super(AbstractIOComponent, self).__init__(*args, **kwargs)
        self.collection_name = 'default'
        self.execution_client.start(Task(handler=self.refresh_config_forever, args=tuple(), period=10))

        # TODO: move this to create index on organization creation
        self.datalake_client.create_index('default', [('attribute_id', 1), ('asset_id', 1), ('timestamp', -1)])
        self.datalake_client.create_index('files', [('timestamp', -1)])
        self.datalake_client.create_index('notification', [('timestamp', -1)])
        self.datalake_client.create_index('BillingEvent', [('timestamp', -1)])
        self.datalake_client.create_index('useractivity', [('timestamp', -1)])

    def _load_hooks(self):
        super()._load_hooks()
        self.datalake_client.add_pre_hook('save', self.hook_rules)
        self.datalake_client.add_pre_hook('save', self.hook_map_variable)

    def hook_rules(self, *args, **kwargs):
        """
        Hook to handle rules and send notifier if a rule applies
        """
        instances = kwargs.get("instances", [])
        variables = [v for v in instances if isinstance(v, Variable)]
        for variable in variables:
            rule = self._hashed_rules.get(f"{variable.asset_id}-{variable.attribute_id}", None)
            if 'value' in variable.args and rule:  # None could be utilized as a value.
                value = variable.args['value']
                if rule.is_satisfied(value):
                    self.notify(
                        notification=Notification(
                            title=rule.message,
                            message=rule.message,
                            severity=rule.severity,
                            asset_id=rule.asset_id,
                            attribute_id=rule.attribute_id,
                            rule_id=rule.id,
                            source_id=self.instance_id,
                            source_type=str(self.managed_class)

                        )
                    )
        return args, kwargs

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

    def refresh_config_forever(self) -> None:
        if self.mapping_class is None:
            logger.debug("No mapping class to refresh")
            return
        logger.debug("Updating mapping in connector")
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
        self.rules = self.database_client.get(
            resource_type=MappingRule,
            asset_id__in=[m.asset_id for m in self.mappings],
            attribute_id__in=[m.attribute_id for m in self.mappings]
        )
        self._hashed_rules = {
            f"{r.asset_id}-{r.attribute_id}": r
            for r in self.rules
        }
        logger.debug(f"Maps found {len(self.mappings)}")
        logger.debug(self.mappings)
        logger.debug(f"Rules found {len(self.rules)}")
        logger.debug(self.rules)


class AbstractClientComponent(AbstractIOComponent):
    mapping_class = ClientMapping

    def __init__(self, *args, **kwargs):
        super(AbstractClientComponent, self).__init__(*args, **kwargs)
        self.type_to_output = {
            float: self.output.FloatValue,
            int: self.output.FloatValue,
            str: self.output.StrValue,
            bool: self.output.BoolValue,
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
