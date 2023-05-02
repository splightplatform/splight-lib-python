from unittest.mock import patch
from uuid import uuid4

import pytest

from splight_lib.models.component import (
    ComponentObject,
    ComponentObjectInstance,
    CustomType,
)
from splight_lib.models.exceptions import InvalidComponentObjectInstance
from splight_lib.settings import settings

settings.configure(LOCAL_ENVIRONMENT=True)


MY_CUSTOM_TYPE = CustomType.parse_obj(
    {
        "name": "MyCustomType",
        "fields": [
            {"name": "float_param", "type": "float"},
            {"name": "str_param", "type": "str"},
            {"name": "int_param", "type": "int"},
        ],
    }
)


def test_invalid_component_object_instance():
    with pytest.raises(InvalidComponentObjectInstance):
        ComponentObjectInstance.list()

    with pytest.raises(InvalidComponentObjectInstance):
        ComponentObjectInstance.retrieve("1234")


def test_from_custom_type_create_model_class_as_expected():
    component_id = str(uuid4())
    model_class = ComponentObjectInstance.from_custom_type(
        MY_CUSTOM_TYPE,
        component_id=component_id,
    )
    assert model_class._schema == MY_CUSTOM_TYPE
    assert model_class._component_id == component_id


@patch.object(ComponentObject, "save", return_value=None)
def test_save(mock):
    component_id = str(uuid4())
    model_class = ComponentObjectInstance.from_custom_type(
        MY_CUSTOM_TYPE,
        component_id=component_id,
    )
    instance = model_class.parse_obj(
        {
            "float_param": 0.5,
            "str_param": "some_param",
            "int_param": 1,
        }
    )
    instance.save()
    mock.assert_called_once()


@patch.object(ComponentObject, "delete", return_value=None)
def test_delete(mock):
    component_id = str(uuid4())
    model_class = ComponentObjectInstance.from_custom_type(
        MY_CUSTOM_TYPE,
        component_id=component_id,
    )
    instance = model_class.parse_obj(
        {
            "id": str(uuid4()),
            "float_param": 0.5,
            "str_param": "some_param",
            "int_param": 1,
        }
    )
    instance.delete()
    mock.assert_called_once()
