from typing import Callable

from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.models.base import SplightDatabaseBaseModel
from splight_lib.models.component import (
    DB_MODEL_TYPE_MAPPING,
    ComponentObject,
    ComponentObjectInstance,
)
from splight_lib.models.event import CommunicationEvent

logger = get_splight_logger()


def database_object_event_handler(
    binding_function: Callable,
    binding_object_type: SplightDatabaseBaseModel,
    event_str: str,
):
    try:
        logger.info(
            "Binding for native object of type %s triggered.",
            binding_object_type,
            tags=LogTags.BINDING,
        )
        event = CommunicationEvent.parse_raw(event_str)
        if binding_object_type in DB_MODEL_TYPE_MAPPING.values():
            # Case in which is not a ComponentObject
            handler_arg = binding_object_type.parse_obj(event.data)
        else:
            # Case for data represents a ComponentObject
            component_obj = ComponentObject.parse_obj(event.data)
            handler_arg = ComponentObjectInstance.from_component_object(
                component_obj
            )
        binding_function(handler_arg)
    except Exception as exc:
        logger.error(
            "Error while handling native object trigger: %s",
            exc,
            exc_info=True,
            tags=LogTags.BINDING,
        )


def __handle_setpoint_trigger(
    binding_function: Callable,
    binding_object_type: SplightDatabaseBaseModel,
    event_str: str,
):
    try:
        logger.debug("Setpoint triggered.", tags=LogTags.SETPOINT)
        object_event = SetPointCreateEvent.parse_raw(event_str)
        setpoint = object_event.data
        response_status = SetPointResponseStatus(binding_function(setpoint))
        if response_status == SetPointResponseStatus.IGNORE:
            return

        setpoint.responses = [
            SetPointResponse(
                component=self.instance_id,
                status=response_status,
            )
        ]
        setpoint_callback_event = SetPointUpdateEvent(data=setpoint)
        self.communication_client.trigger(setpoint_callback_event)
    except Exception as exc:
        logger.error(
            "Error while handling setpoint create: %s",
            exc,
            exc_info=True,
            tags=LogTags.SETPOINT,
        )
