from typing import Dict

import pytest
from pydantic import ValidationError

from splight_lib.execution.exceptions import InvalidCronString
from splight_lib.execution.scheduling import Crontab


@pytest.mark.parametrize(
    "parameters",
    [
        {"month": 0},
        {"month": 13},
        {"day_of_week": 8},
        {"hour": 24},
        {"minute": 60},
        {"second": 90},
    ],
)
def test_crontab_creation_outside_range(parameters: Dict):
    with pytest.raises(ValidationError):
        _ = Crontab.model_validate(parameters)


@pytest.mark.parametrize(
    "cron_str",
    [
        "* * * * * *",
        "* */2",
    ],
)
def test_create_crontab_from_str_error(cron_str: str):
    with pytest.raises(InvalidCronString):
        _ = Crontab.from_string(cron_str)


@pytest.mark.parametrize(
    "cron_str,output",
    [
        (
            "* * * * *",
            {
                "month": "*",
                "day": "*",
                "day_of_week": "*",
                "hour": "*",
                "minute": "*",
            },
        ),
        (
            "*/1 * * * *",
            {
                "month": "*",
                "day": "*",
                "day_of_week": "*",
                "hour": "*",
                "minute": "*/1",
            },
        ),
        (
            "*/1 * 2 * *",
            {
                "month": "*",
                "day": 2,
                "day_of_week": "*",
                "hour": "*",
                "minute": "*/1",
            },
        ),
        (
            "* * * 3 3",
            {
                "month": 3,
                "day": "*",
                "day_of_week": 3,
                "hour": "*",
                "minute": "*",
            },
        ),
    ],
)
def test_create_crontab_from_string(cron_str: str, output: Dict):
    crontab = Crontab.from_string(cron_str)
    assert crontab.model_dump(exclude_none=True) == output
