import os

import pytest
from pydantic import ValidationError

os.environ["SPLIGHT_ACCESS_ID"] = "access_id"
os.environ["SPLIGHT_SECRET_KEY"] = "secret_key"

from splight_lib.models import Metadata  # noqa: E402


@pytest.mark.parametrize(
    "value_type,value,expected",
    [
        ("Number", 1, int),
        ("Number", 0.5, float),
        ("Number", "2", int),
        ("Number", "0.4", float),
        ("String", 2, str),
        ("String", True, str),
        ("String", False, str),
        ("Boolean", 1, bool),
        ("Boolean", 0, bool),
        ("Boolean", "string", bool),
    ],
)
def test_cast_value(value_type, value, expected):
    model = Metadata(name="metadata", type=value_type, value=value)
    assert isinstance(model.value, expected)


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, False),
        ("", False),
        (1, True),
        (0.5, True),
        ("asdf", True),
        (None, None),
    ],
)
def test_cast_bool(value, expected):
    model = Metadata(name="metadata", type="Boolean", value=value)
    assert model.value == expected


@pytest.mark.parametrize(
    "value_type,value",
    [
        ("Number", True),
        ("Number", False),
        ("Number", "string"),
    ],
)
def test_wrong_type(value_type, value):
    with pytest.raises(ValidationError):
        Metadata(name="metadata", type=value_type, value=value)
