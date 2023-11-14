import os
import sys
from abc import ABC, abstractmethod
from collections import namedtuple
from functools import partial
from tempfile import NamedTemporaryFile
from time import sleep
from typing import Callable, Dict, List, Optional, Type

from pydantic import BaseModel

from splight_lib.client.communication import RemoteCommunicationClient
from splight_lib.communication.event_handler import (
    command_event_handler,
    database_object_event_handler,
)
from splight_lib.component.exceptions import (
    InvalidBidingObject,
    MissingBindingCallback,
    MissingCommandCallback,
    MissingRoutineCallback,
)
from splight_lib.component.spec import Spec

# TODO: Use builder pattern
from splight_lib.execution import ExecutionClient, Thread
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.models.component import (
    DB_MODEL_TYPE_MAPPING,
    Binding,
    Command,
    ComponentObjectInstance,
    Routine,
    RoutineObject,
    RoutineObjectInstance,
)
from splight_lib.models.event import EventNames
from splight_lib.restclient import ConnectError, HTTPError, Timeout
from splight_lib.settings import settings

REQUEST_EXCEPTIONS = (ConnectError, HTTPError, Timeout)
logger = get_splight_logger("Base Component")


class HealthCheckProcessor:
    _HEALTHCHECK_INTERVAL = 10
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
            is_alive, status = self._engine.healthcheck()
            if not is_alive:
                exc = self._engine.get_last_exception()
                self._log_exception(exc)
                self._logger.info("Healthcheck finished", tags=LogTags.RUNTIME)
                self._health_file.close()
                self._logger.info(
                    "Healthcheck file removed: %s",
                    self._health_file,
                    tags=LogTags.RUNTIME,
                )
                break
            sleep(self._HEALTHCHECK_INTERVAL)

    def stop(self):
        self._running = False

    def _log_exception(self, exc: Optional[Exception]) -> None:
        """Logs the exception and the traceback."""
        if exc:
            stack = exc.__traceback__
            exc_type = type(exc)
            self._logger.exception(exc, exc_info=(exc_type, exc, stack))


class SplightBaseComponent(ABC):
    def __init__(
        self,
        component_id: Optional[str] = None,
    ):
        self._component_id = component_id

        # TODO: Change to use builder patter
        self._comm_client = RemoteCommunicationClient(
            url=settings.SPLIGHT_PLATFORM_API_HOST,
            access_id=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
            instance_id=component_id,
        )
        self._execution_engine = ExecutionClient()
        self._health_check = HealthCheckProcessor(self._execution_engine)
        self._health_check_thread = Thread(
            target=self._health_check.start, args=(), daemon=False
        )

        self._spec = self._load_spec()
        self._input = self._spec.component_input(component_id)
        self._output = self._spec.get_output_models(component_id)

        component_objects = {
            ct.name: ComponentObjectInstance.from_custom_type(
                ct, component_id=component_id
            )
            for ct in self._spec.custom_types
        }
        routine_objects = {
            routine.name: RoutineObjectInstance.from_routine(
                routine, component_id=self._component_id
            )
            for routine in self._spec.routines
        }

        # TODO: check if we are going to still use binding
        bindings = [
            binding
            for binding in self._spec.bindings
            if binding.object_type != "SetPoint"
        ]
        self._load_bindings(bindings, component_objects)
        self._load_routines(self._spec.routines, routine_objects)
        self._load_commands(self._spec.commands)
        self._custom_types = self._get_custom_type_model(component_objects)
        self._routines = self._get_routine_model(routine_objects)

        self.start = self._wrap_start(self.start)

    @property
    def input(self) -> BaseModel:
        return self._input

    @property
    def output(self) -> BaseModel:
        return self._output

    @property
    def routines(self) -> Type:
        return self._routines

    @property
    def custom_types(self) -> BaseModel:
        return self._custom_types

    @property
    def execution_engine(self) -> ExecutionClient:
        return self._execution_engine

    def _register_exit(self):
        if self._execution_engine.get_last_exception():
            sys.exit(1)
        else:
            sys.exit(0)

    def _wrap_start(self, original_start: Callable) -> Callable:
        """Wraps the start method to wait for all threads to finish.

        Parameters
        ----------
        original_start: Callable
            The implemented start method from the component

        Returns
        -------
        Callable
            The start method wrapped
        """

        def wrapper():
            # We can't add the healthcheck thread into the execution engine
            # because that thread should stop if any of the registered threads
            # is stopped.
            # Also, we start the healthcheck thread when the method start is
            # called, this way if there is any error on the initialization we
            # can get that error and the component will fail
            self._health_check_thread.start()
            try:
                original_start()
            except Exception as exc:
                logger.exception(exc, tags=LogTags.COMPONENT)
                self._health_check.stop()
                self._execution_engine.terminate_all()
                sys.exit(1)

            for thread in self._execution_engine.threads:
                thread.join()

            self._health_check.stop()
            self._health_check_thread.join()
            self._register_exit()

        return wrapper

    def _get_custom_type_model(
        self, component_object: Dict[str, Type[ComponentObjectInstance]]
    ) -> BaseModel:
        custom_type_model = namedtuple(
            "CustomTypes", [k for k in component_object.keys()]
        )
        return custom_type_model(**component_object)

    def _get_routine_model(
        self, routine_objects: Dict[str, Type[RoutineObjectInstance]]
    ) -> namedtuple:
        routine_model = namedtuple(
            "ComponentRoutine", [k for k in routine_objects.keys()]
        )
        return routine_model(**routine_objects)

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
        component_objects: Dict[str, Type[ComponentObjectInstance]],
    ):
        """Loads and assigns callbacks for the bindings."""
        for binding in bindings:
            type_ = binding.object_type
            model_class = DB_MODEL_TYPE_MAPPING.get(
                type_, component_objects.get(type_)
            )
            if not model_class:
                raise InvalidBidingObject(model_class.__name__)
            event_name = model_class.get_event_name(
                model_class.__name__, binding.object_action
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

    def _load_routines(
        self,
        routines: List[Routine],
        routines_objects: Dict[str, Type[RoutineObjectInstance]],
    ) -> None:
        """Loads and assigns callbacks to the routines."""

        actions = ["create", "update", "delete"]
        for routine in routines:
            model_calss = routines_objects.get(routine.name)

            for action in actions:
                event_name = RoutineObject.get_event_name(
                    model_calss.__name__, action
                )

                callback_func = getattr(
                    self, getattr(routine, f"{action}_handler"), None
                )
                if not callback_func:
                    raise MissingRoutineCallback(routine.name, action)
                self._comm_client.bind(
                    event_name,
                    partial(
                        database_object_event_handler,
                        callback_func,
                        model_calss,
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

    @abstractmethod
    def start(self):
        raise NotImplementedError()

    def stop(self):
        self._execution_engine.terminate_all()
        sys.exit(1)
