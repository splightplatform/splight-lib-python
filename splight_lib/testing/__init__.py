import os
from datetime import datetime
from typing import Any, Dict, List

import pytest
from pytest_mock import MockerFixture

from splight_lib.component.spec import Spec
from splight_lib.models import (
    Asset,
    Attribute,
    Component,
    ComponentObjectInstance,
    File,
)
from splight_lib.models.component import CustomType, Parameter

FAKE_NATIVE_VALUES = {
    "int": 1,
    "bool": True,
    "str": "fake",
    "float": 5.5,
    "datetime": datetime(2022, 12, 18),
    "url": "www.google.com",
}

FAKE_DATABASE_VALUES = {
    "Component": Component(name="ComponentTest", version="1.0.0"),
    "Asset": Asset(name="AssetTest"),
    "Attribute": Attribute(name="AttrTest"),
    "File": File(file=""),
}


def get_test_value(type_: str, custom_types: Dict[str, CustomType]) -> Any:
    if type_ in FAKE_NATIVE_VALUES:
        value = FAKE_NATIVE_VALUES.get(type_)
    elif type_ in FAKE_DATABASE_VALUES:
        value = FAKE_DATABASE_VALUES.get(type_)
    else:
        custom_type_def = custom_types[type_]
        model_class = ComponentObjectInstance.from_custom_type(custom_type_def)
        aux_value = component_object_attributes(
            custom_type_def.fields, custom_types
        )
        value = model_class.model_validate(aux_value)
    return value


def component_object_attributes(
    parameters: List[Parameter], custom_types: Dict[str, CustomType]
) -> Dict[str, Any]:
    values_dict = {
        param.name: get_test_value(param.type, custom_types)
        for param in parameters
    }
    return values_dict


def get_test_input(spec: Spec):
    input_model_class = spec.get_input_model()
    custom_types = {ct.name: ct for ct in spec.custom_types}
    input_fake_values = {}
    for param in spec.input:
        param_name = param.name
        type_ = param.type
        value = get_test_value(type_, custom_types)

        if param.multiple:
            value = [value]

        input_fake_values.update({param_name: value})
    return input_model_class.model_validate(input_fake_values)


@pytest.fixture(autouse=True)
def mock_component(mocker: MockerFixture):
    # Patch method for checking duplicated component
    mocker.patch(
        (
            "splight_lib.component.abstract.SplightBaseComponent."
            "_check_duplicated_component"
        ),
        return_value=None,
    )

    # Patch HealthCheckProcessor
    mocker.patch(
        "splight_lib.execution.ExecutionClient.start", return_value=None
    )

    base_path = os.getcwd()
    spec = Spec.from_file(os.path.join(base_path, "spec.json"))
    # Generate fake input for testing
    mocker.patch(
        "splight_lib.component.spec.Spec.component_input",
        return_value=get_test_input(spec),
    )
    return mocker
