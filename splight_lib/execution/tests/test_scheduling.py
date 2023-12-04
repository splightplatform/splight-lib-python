from typing import Dict

import pytest
from pydantic import ValidationError

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
