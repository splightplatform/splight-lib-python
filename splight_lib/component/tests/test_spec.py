from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

from splight_lib.component.spec import InputParameter, Spec


@pytest.mark.parametrize(
    "input_parameters,expected_model_data",
    [
        (
            [
                InputParameter(
                    name="param1",
                    type="str",
                    required=False,
                    description="Test param1",
                    multiple=False,
                    sensitive=False,
                    value="test",
                )
            ],
            {"param1": {"type": str, "value": "test", "required": False}},
        ),  # single parameter
        (
            [
                InputParameter(
                    name="param1",
                    type="str",
                    required=False,
                    description="Test param1",
                    multiple=False,
                    sensitive=False,
                    value="test",
                ),
                InputParameter(
                    name="param2",
                    type="int",
                    required=True,
                    description="Test param2",
                    multiple=False,
                    sensitive=False,
                    value=123,
                ),
            ],
            {
                "param1": {"type": str, "value": "test", "required": False},
                "param2": {"type": int, "value": 123, "required": True},
            },
        ),  # multiple parameters
        ([], {}),  # no parameters
    ],
)
def test_get_input_model(
    input_parameters: List[InputParameter],
    expected_model_data: Dict[str, Dict],
):
    spec = Spec(
        name="TestSpec",
        version="1.0.0",
        splight_cli_version="2.3.1",
        input=input_parameters,
    )
    input_model_class = spec.get_input_model()

    # Check that the created model has the correct attributes
    assert set(input_model_class.__annotations__.keys()) == set(
        expected_model_data.keys()
    )

    # Create an instance of the model with the given values
    instance = input_model_class(
        **{key: data["value"] for key, data in expected_model_data.items()}
    )

    # Check that the created model instance has the correct attributes with correct types
    for key, data in expected_model_data.items():
        assert isinstance(getattr(instance, key, None), data["type"])

    # Check Config settings
    assert input_model_class.Config.use_enum_values is True

    # Check that the created model behaves correctly with valid and invalid inputs
    assert isinstance(instance, input_model_class)

    if any(
        param.required
        for param in input_parameters
        if param.name in expected_model_data
    ):
        with pytest.raises(ValidationError):
            input_model_class(
                **{
                    key: None
                    for key, data in expected_model_data.items()
                    if not data["required"]
                }
            )


@patch("splight_lib.models.Component.retrieve")
@patch("splight_lib.component.spec.Spec.get_input_model")
def test_component_input(mock_get_input_model, mock_retrieve):
    # Create an instance of the class we're testing
    spec = Spec(
        name="TestSpec", version="1.0.0", splight_cli_version="2.3.1", input=[]
    )

    # Setup the mock Component and InputModel
    mock_component = MagicMock()
    mock_input_model = MagicMock()

    mock_input_param = InputParameter(
        name="param1",
        type="str",
        required=False,
        description="Test param1",
        multiple=False,
        sensitive=False,
        value="test",
    )

    # The mock Component's input should return our mocked InputParameter
    mock_component.input = [mock_input_param]

    # Creating a mock spec'd to BaseModel
    mock_base_model_instance = MagicMock(spec=BaseModel)
    mock_input_model.parse_obj.return_value = mock_base_model_instance

    # Spec.get_input_model() should return our mock model
    mock_get_input_model.return_value = mock_input_model

    # Component.retrieve() should return our mock component
    mock_retrieve.return_value = mock_component

    # Test the method
    result = spec.component_input("test_id")

    # Check that Spec.get_input_model() and Component.retrieve() were called with the correct arguments
    mock_get_input_model.assert_called_once()
    mock_retrieve.assert_called_once_with("test_id")

    # Check that the result is an instance of the correct class
    assert isinstance(result, BaseModel)

    # Check that the input_model.parse_obj() was called with the correct arguments
    mock_input_model.parse_obj.assert_called_once_with({"param1": "test"})
