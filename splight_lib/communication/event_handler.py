from typing import Callable, Type

from splight_lib.client.communication.abstract import (
    AbstractCommunicationClient,
)
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.models.base import SplightDatabaseBaseModel
from splight_lib.models.component import (
    DB_MODEL_TYPE_MAPPING,
    Command,
    ComponentObject,
    ComponentObjectInstance,
    RoutineObject,
    RoutineObjectInstance,
    get_field_value,
)
from splight_lib.models.event import (
    CommunicationEvent,
    ComponentCommand,
    ComponentCommandStatus,
    ComponentCommandTriggerEvent,
    ComponentCommandUpdateEvent,
)

logger = get_splight_logger()


class InvalidCommandResponse(Exception):
    pass


class InvalidBidingObject(Exception):
    pass


def database_object_event_handler(
    binding_function: Callable,
    binding_object_type: Type[SplightDatabaseBaseModel],
    event_str: str,
):
    """General handler for database events used for Component Bindings.

    Parameters
    ----------
    binding_function: Callable
        Function to be executed.
    binding_object_type: Type[SplightDatabaseBaseModel]
        The class for the object associated with the binding event.
    event_str:
        The raw event string from pusher client.
    """
    try:
        logger.info(
            f"Binding for object of type {binding_object_type} triggered.",
            tags=LogTags.BINDING,
        )
        event = CommunicationEvent.parse_raw(event_str)
        if binding_object_type in DB_MODEL_TYPE_MAPPING.values():
            # Case in which is not a ComponentObject
            handler_arg = binding_object_type.model_validate(event.data)
        elif issubclass(binding_object_type, ComponentObjectInstance):
            # Case for data represents a ComponentObject
            component_obj = ComponentObject.model_validate(event.data)
            model_class = ComponentObjectInstance.from_object(component_obj)
            handler_arg = model_class.parse_object(component_obj)
        elif issubclass(binding_object_type, RoutineObjectInstance):
            # Case for data represents a RoutineObject
            routine_obj = RoutineObject.model_validate(event.data)
            model_class = RoutineObjectInstance.from_object(routine_obj)
            handler_arg = model_class.parse_object(routine_obj)
        else:
            raise InvalidBidingObject(
                f"Invalid binding object type: {binding_object_type}"
            )

        binding_function(handler_arg)
    except Exception as exc:
        logger.error(
            "Error while handling native object trigger: %s",
            exc,
            exc_info=True,
            tags=LogTags.BINDING,
        )


def command_event_handler(
    binding_function: Callable,
    comm_client: AbstractCommunicationClient,
    event_str: str,
):
    """General handler for component's commands events.

    Parameters
    ----------
    binding_function: Callable
        Function to be executed.
    comm_client: AbstractCommunicationClient
        Communication client to send command response.
    event_str:
        The raw event string from pusher client.
    """
    component_command_event = ComponentCommandTriggerEvent.parse_raw(event_str)
    component_command: ComponentCommand = component_command_event.data
    command: Command = component_command.command
    logger.info(
        "Binding for component command '%s' triggered.",
        command.name,
        tags=LogTags.COMMAND,
    )
    try:
        fields = {
            field.name: get_field_value(field) for field in command.fields
        }
        command_output = binding_function(**fields)
        if not isinstance(command_output, str):
            raise InvalidCommandResponse("Command output is not a string")

        component_command.response.return_value = command_output
        component_command.status = ComponentCommandStatus.SUCCESS
    except Exception as exc:
        logger.error(
            "Error while handling component command trigger: %s",
            exc,
            exc_info=True,
            tags=LogTags.COMMAND,
        )
        component_command.response.error_detail = str(exc)
        component_command.status = ComponentCommandStatus.ERROR
    component_command_callback_event = ComponentCommandUpdateEvent(
        data=component_command
    )
    comm_client.trigger(component_command_callback_event)
