import os
from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from splight_lib.component.spec import Spec
from splight_lib.models import Asset, Attribute, Component, File

FAKE_NATIVE_TYPES = {
    "int": 1,
    "bool": True,
    "str": "fake",
    "float": 5.5,
    "datetime": datetime(2022, 12, 18),
    "url": "www.google.com",
}

FAKE_DATABASE_TYPES = {
    "Component": Component(name="ComponentTest", version="1.0.0"),
    "Asset": Asset(name="AssetTest"),
    "Attribute": Attribute(name="AttrTest"),
    "File": File(file=""),
}


def get_test_input(spec: Spec):
    input_model_class = spec.get_input_model()
    input_fake_values = {}
    for param in spec.input:
        param_name = param.name
        type_ = param.type

        if type_ in FAKE_NATIVE_TYPES:
            value = FAKE_NATIVE_TYPES.get(type_)
        elif type_ in FAKE_DATABASE_TYPES:
            value = FAKE_DATABASE_TYPES.get(type_)
            value.save()
        # TODO: Add ComponentObject in input

        if param.multiple:
            value = [value]

        input_fake_values.update({param_name: value})
    return input_model_class.parse_obj(input_fake_values)


@pytest.fixture
def mock_component(mocker: MockerFixture):
    os.environ["LOCAL_ENVIRONMENT"] = "True"
    mocker.patch(
        (
            "splight_lib.component.abstract.SplightBaseComponent."
            "_check_duplicated_component"
        ),
        return_value=None,
    )

    # TODO: This patch is not working as expected
    mocker.patch(
        "splight_lib.execution.ExecutionClient.start", return_value=None
    )

    base_path = os.getcwd()
    spec = Spec.from_file(os.path.join(base_path, "spec.json"))
    mocker.patch(
        "splight_lib.component.spec.Spec.component_input",
        return_value=get_test_input(spec),
    )
    return mocker
