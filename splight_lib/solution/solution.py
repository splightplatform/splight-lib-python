import json
import os

from splight_lib.models import Solution
from splight_lib.solution.exceptions import (
    MissingInstanceEnvVar,
    MissingInstanceId,
)

ENV_VAR = "INSTANCE_AS_STR"


class SolutionLoader:
    @classmethod
    def from_env(cls) -> Solution:
        if not (str_instance := os.environ.get(ENV_VAR)):
            raise MissingInstanceEnvVar(ENV_VAR)
        str_instance = os.environ.get("INSTANCE_AS_STR", "")
        instance = json.loads(str_instance)
        if not (instance_id := instance.get("id")):
            raise MissingInstanceId()
        solution = Solution.retrieve(instance_id)
        return solution
