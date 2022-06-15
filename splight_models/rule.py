import builtins
import operator
from .base import SplightBaseModel
from os import stat  # noqa
import re
import math
from collections import defaultdict
from enum import Enum
from pydoc import locate
from pydantic import validator
from typing import Optional, List, Dict
from .common import SeverityType
from splight_database.django.djatabase.models.constants import (
    EQUAL, GREATER_THAN, GREATER_THAN_OR_EQUAL, LOWER_THAN, LOWER_THAN_OR_EQUAL
)


def _safe_eval(expression):
    # Raises on syntax error
    ALLOWED_NAMES = {
        key: value
        for key, value in math.__dict__.items()
        if not key.startswith("__")
    }
    code = compile(expression, "<string>", "eval")
    compilation_errors = [
        name
        for name in code.co_names
        if name not in ALLOWED_NAMES
    ]
    if compilation_errors:
        raise NameError(f"The use of {','.join(compilation_errors)} is not allowed")
    return eval(code, {"__builtins__": {}}, ALLOWED_NAMES)


class RuleVariableType(str, Enum):
    str = 'str'
    float = 'float'
    bool = 'bool'


class RuleVariable(SplightBaseModel):
    id: str
    collection: str = 'default'
    filters: Dict = {}
    key: str = "args.value"
    type: RuleVariableType = RuleVariableType.str


class AlgorithmRule(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    variables: List[RuleVariable] = []
    statement: str

    @staticmethod
    def statement_evaluation(statement, variables: List, values: Dict) -> bool:
        _variables = {}
        # Parse variables
        for var in variables:
            _type = locate(var.type)
            _default_value = _type()
            _value = values.get(var.id)
            _casted_value = _type(_value) if _value else _default_value
            _variables[re.escape(var.id)] = repr(_casted_value)
        # Replace ONLY if needed
        if _variables:
            _pattern = re.compile("|".join(_variables.keys()))
            statement = _pattern.sub(lambda m: _variables[re.escape(m.group(0))], statement)
        return _safe_eval(statement)

    @validator('statement', always=True)
    def statement_validate(cls, statement, values):
        try:
            cls.statement_evaluation(statement, values.get('variables'), defaultdict(int))
        except (SyntaxError, NameError):
            raise ValueError("Invalid syntax")
        return statement


class OperatorType(str, Enum):
    greater_than = GREATER_THAN
    greater_than_or_equal = GREATER_THAN_OR_EQUAL
    lower_than = LOWER_THAN
    lower_than_or_equal = LOWER_THAN_OR_EQUAL
    equal = EQUAL


class MappingRule(SplightBaseModel):
    id: Optional[str]
    asset_id: str
    attribute_id: str
    value: str
    type: RuleVariableType = RuleVariableType.str
    message: str
    severity: SeverityType = SeverityType.info
    operator: OperatorType = OperatorType.equal

    @property
    def name(self):
        return self.value

    @property
    def description(self):
        return self.message

    def is_satisfied(self, value):
        rule_value = getattr(builtins, self.type)(self.value)
        value = getattr(builtins, self.type)(value)
        return getattr(operator, self.operator)(rule_value, value)
