import os
import warnings

os.environ["SPLIGHT_ACCESS_ID"] = "access_id"
os.environ["SPLIGHT_SECRET_KEY"] = "secret_key"

from unittest.mock import patch  # noqa: E402
from uuid import uuid4  # noqa: E402

import pytest  # noqa: E402

from splight_lib.models.component import (  # noqa: E402
    ComponentObject,
    ComponentObjectInstance,
    CustomType,
)
from splight_lib.models.exceptions import InvalidObjectInstance  # noqa: E402
from splight_lib.settings import settings  # noqa: E402

settings.configure(LOCAL_ENVIRONMENT=True)
warnings.filterwarnings("ignore", category=RuntimeWarning)


MY_CUSTOM_TYPE = CustomType.model_validate(
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
    with pytest.raises(InvalidObjectInstance):
        ComponentObjectInstance.list()

    with pytest.raises(InvalidObjectInstance):
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
    instance = model_class.model_validate(
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
    instance = model_class.model_validate(
        {
            "id": str(uuid4()),
            "float_param": 0.5,
            "str_param": "some_param",
            "int_param": 1,
        }
    )
    instance.delete()
    mock.assert_called_once()
