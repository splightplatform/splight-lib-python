import os
import sys
from abc import ABC, abstractmethod
from collections import namedtuple
from tempfile import NamedTemporaryFile
from threading import Thread
from time import sleep
from typing import Callable, Dict, Optional, Type

from pydantic import BaseModel
from pydantic_core import ValidationError

from splight_lib.component.spec import Spec
from splight_lib.execution.engine import EngineStatus, ExecutionEngine
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.models.component import (
    ComponentObjectInstance,
    RoutineObjectInstance,
)
from splight_lib.restclient import ConnectError, HTTPError, Timeout

REQUEST_EXCEPTIONS = (ConnectError, HTTPError, Timeout)
logger = get_splight_logger("Base Component")


class HealthCheckProcessor:
    HEALTHCHECK_INTERVAL = 5
    _HEALTH_FILE_PREFIX = "healthy_"
    _STARTUP_FILE_PREFIX = "ready_"

    def __init__(self, engine: ExecutionEngine):
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
        # Check when there is no task in engine
        while self._running:
            is_running, _ = self._engine.healthcheck()
            if not is_running:
                self._logger.info("Healthcheck finished", tags=LogTags.RUNTIME)
                self._health_file.close()
                self._logger.info(
                    "Healthcheck file removed: %s",
                    self._health_file,
                    tags=LogTags.RUNTIME,
                )
                break
            sleep(self.HEALTHCHECK_INTERVAL)

    def stop(self):
        self._running = False


class SplightBaseComponent(ABC):
    def __init__(
        self,
        component_id: Optional[str] = None,
    ):
        self._component_id = component_id
        self._execution_engine = ExecutionEngine()
        self._health_check = HealthCheckProcessor(self._execution_engine)
        self._health_check_thread = Thread(
            target=self._health_check.start,
            args=(),
            daemon=False,
        )

        self._spec = None
        self._input = None
        self._output = None
        self._custom_types = None
        self._routines = None
        try:
            self._setup_component(component_id)
        except ValidationError as exc:
            logger.debug(
                "There was an error validating the component configuration"
            )
            logger.exception(exc, tags=LogTags.COMPONENT)
            self.stop()
        except Exception as exc:
            logger.exception(exc, tags=LogTags.COMPONENT)
            self.stop()

        self.start = self._wrap_start(self.start)

    def _setup_component(self, component_id: str):
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
        self._custom_types = self._get_custom_type_model(component_objects)
        self._routines = self._get_routine_model(routine_objects)

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
    def execution_engine(self) -> ExecutionEngine:
        return self._execution_engine

    def _register_exit(self):
        if self._execution_engine.state == EngineStatus.FAILED:
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
                self._execution_engine.stop()
                sys.exit(1)

            # Wait for healthcheck to update before stopping everything
            sleep(HealthCheckProcessor.HEALTHCHECK_INTERVAL)
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

    @abstractmethod
    def start(self):
        raise NotImplementedError()

    def stop(self):
        self._execution_engine.stop()
        sys.exit(1)
