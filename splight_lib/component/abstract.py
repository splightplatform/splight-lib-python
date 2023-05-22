import os
import sys
from functools import partial
from tempfile import NamedTemporaryFile
from threading import Thread
from time import sleep
from typing import Dict, List, Optional

from furl import furl
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
from splight_lib.logging._internal import LogTags, get_splight_logger
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


class HealthCheckProcessor:
    _HEALTHCHECK_INTERVAL = 5
    _HEALTH_FILE_PREFIX = "healthy_"
    _STARTUP_FILE_PREFIX = "ready_"

    def __init__(self, engine: ExecutionClient):
        self._logger = get_splight_logger("HealthCheckProcessor")
        self._engine = engine
        self._health_file = NamedTemporaryFile(prefix=self._HEALTH_FILE_PREFIX)
        self._startup_file = NamedTemporaryFile(
            prefix=self._STARTUP_FILE_PREFIX
        )
        self._running = False
        self._logger.info(
            "Healthcheck file at: %s",
            self._health_file.name,
            tags=LogTags.RUNTIME,
        )
        self._logger.info(
            "Startup file at: %s",
            self._startup_file.name,
            tags=LogTags.RUNTIME,
        )

    def start(self):
        self._running = True
        while self._running:
            if not self._engine.healthcheck():
                self._logger.error(
                    "Healthcheck task failed.", tags=LogTags.RUNTIME
                )
                self._health_file.close()
                self._logger.error(
                    "Healthcheck file removed: %s",
                    self._health_file,
                    tags=LogTags.RUNTIME,
                )
                sys.exit(1)
            sleep(self._HEALTHCHECK_INTERVAL)

    def stop(self):
        self._running = False


class SplightBaseComponent:
    def __init__(
        self,
        component_id: Optional[str] = None,
    ):
        self._component_id = component_id

        if not settings.LOCAL_ENVIRONMENT:
            self._check_duplicated_component()
        # TODO: Change to use builder patter
        self._comm_client = RemoteCommunicationClient(
            url=settings.SPLIGHT_PLATFORM_API_HOST,
            access_id=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            instance_id=component_id,
        )
        self._execution_engine = ExecutionClient()
        health_check = HealthCheckProcessor(self._execution_engine)
        self._health_check_thread = Thread(
            target=health_check.start, args=(), daemon=True
        )
        self._execution_engine.start(self._health_check_thread)

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

    @property
    def output(self) -> BaseModel:
        return self._output

    @property
    def execution_engine(self) -> ExecutionClient:
        return self._execution_engine

    def _load_spec(self) -> Spec:
        """Loads the spec.json files located at the same level that the
        main file.
        """
        base_path = os.getcwd()
        spec = Spec.from_file(os.path.join(base_path, "spec.json"))
        return spec

    def _load_bindings(
        self,
        bindings: List[Binding],
        component_objects: Dict[str, ComponentObjectInstance],
    ):
        """Loads and assigns callbacks for the bindings."""
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
        """Loads and assigns callbacks to the setpoing."""
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
        """Assigns callbacks function to each of the defined commands."""
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
        base_url = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        base_path = "v2/engine/component/components"
        api_url = base_url / f"{base_path}/{self._component_id}/connections/"
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
        self._execution_engine.stop(self._health_check_thread)
        self._execution_engine.terminate_all()
        sys.exit(1)
