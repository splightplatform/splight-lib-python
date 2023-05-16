import os
from functools import partial
from typing import Dict, List, Optional

from pydantic import BaseModel
from retry import retry

from splight_lib.auth import SplightAuthToken
# TODO: Use builder pattern
from splight_lib.client.communication import RemoteCommunicationClient
from splight_lib.communication.event_handler import (
    command_event_handler,
    database_object_event_handler,
    setpoint_event_handler,
)
from splight_lib.component.exceptions import (
    DuplicatedComponentException,
    InvalidBidingObject,
    MissingBindingCallback,
    MissingCommandCallback,
    MissingSetPointCallback,
)
from splight_lib.component.spec import Spec
from splight_lib.execution import ExecutionClient
from splight_lib.models.component import (
    DB_MODEL_TYPE_MAPPING,
    Binding,
    Command,
    ComponentObjectInstance,
)
from splight_lib.models.event import EventNames
from splight_lib.models.setpoint import SetPoint
from splight_lib.restclient import (
    ConnectError,
    HTTPError,
    SplightRestClient,
    Timeout,
)
from splight_lib.settings import settings

REQUEST_EXCEPTIONS = (ConnectError, HTTPError, Timeout)


class SplightBaseComponent:
    def __init__(
        self,
        component_id: Optional[str] = None,
        local_environment: bool = False,
    ):
        # TODO settings managment
        settings.configure(LOCAL_ENVIRONMENT=local_environment)
        self._component_id = component_id

        self._comm_client = RemoteCommunicationClient(instance_id=component_id)
        self._execution_engine = ExecutionClient()
        if not local_environment:
            self._check_duplicated_component()

        self._spec = self._load_spec()
        self._input = self._spec.component_input(component_id)
        self._output = self._spec.get_output_models(component_id)

        component_objects = {
            ct.name: ComponentObjectInstance.from_custom_type(
                ct, component_id=component_id
            )
            for ct in self._spec.custom_types
        }

        bindings = [
            binding
            for binding in self._spec.bindings
            if binding.object_type != "SetPoint"
        ]
        setpoints = [
            binding
            for binding in self._spec.bindings
            if binding.object_type == "SetPoint"
        ]
        self._load_bindings(bindings, component_objects)
        self._load_setpoints(setpoints)
        self._load_commands(self._spec.commands)

    @property
    def input(self) -> BaseModel:
        return self._input

    def _load_spec(self) -> Spec:
        base_path = os.getcwd()
        spec = Spec.from_file(os.path.join(base_path, "spec.json"))
        return spec

    def _load_bindings(
        self,
        bindings: List[Binding],
        component_objects: Dict[str, ComponentObjectInstance],
    ):
        for binding in bindings:
            type_ = binding.object_type
            model_class = DB_MODEL_TYPE_MAPPING.get(
                type_, component_objects.get(type_)
            )
            if not model_class:
                raise InvalidBidingObject(model_class.__class__.__name__)
            event_name = model_class.get_event_name(
                model_class.__class__.__name__, binding.object_action
            )
            callback_func = getattr(self, binding.name, None)
            if not callback_func:
                raise MissingBindingCallback(binding.name)

            self._comm_client.bind(
                event_name,
                partial(
                    database_object_event_handler,
                    callback_func,
                    model_class,
                ),
            )

    def _load_setpoints(self, setpoints: List[SetPoint]):
        for setpoint in setpoints:
            event_name = SetPoint.get_event_name(
                SetPoint.__name__, setpoint.object_action
            )
            callback_func = getattr(self, setpoint.name, None)
            if not callback_func:
                raise MissingSetPointCallback(setpoint.name)

            self._comm_client.bind(
                event_name,
                partial(
                    setpoint_event_handler,
                    callback_func,
                    self._comm_client,
                    self._component_id,
                ),
            )

    def _load_commands(self, commands: List[Command]):
        for command in commands:
            callback_func = getattr(self, command.name.lower(), None)
            if not callback_func:
                raise MissingCommandCallback(command.name)
            event_name = (EventNames.COMPONENTCOMMAND_TRIGGER.value,)
            self._comm_client.bind(
                event_name,
                partial(
                    command_event_handler,
                    callback_func,
                    self._comm_client,
                ),
            )

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _check_duplicated_component(self):
        """
        Validates that there are no other connections to communication client
        """
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        rest_client = SplightRestClient()
        rest_client.update_headers(token.header)
        url_path = f"component/components/{self._component_id}/connections/"
        api_url = f"{settings.SPLIGHT_PLATFORM_API_HOST}/v2/engine/{url_path}"
        response = rest_client.get(api_url)
        if response.status_code == 200:
            connections = response.json()["subscription_count"]
            if int(connections) > 0:
                raise DuplicatedComponentException(self._component_id)
        else:
            raise Exception(
                (
                    "Error checking if component is already running. "
                    f"Status: {response.status_code}"
                )
            )

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()
