import re
import math
from collections import defaultdict
from enum import Enum
from pydoc import locate
from xmlrpc.client import Boolean
from pydantic import BaseModel, validator
from typing import Optional, List, Dict


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
    int = 'int'
    bool = 'bool'


class RuleVariable(BaseModel):
    id: str
    collection: str = 'default'
    filters: Dict = {}
    key: str = "args.value"
    type: RuleVariableType = RuleVariableType.str


class Rule(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    variables: List[RuleVariable] = []
    statement: str

    @staticmethod
    def statement_evaluation(statement, variables: List, values: Dict) -> Boolean:
        _variables = defaultdict(int)
        for var in variables:
            _type = locate(var.type)
            _default_value = _type()
            _value = values.get(var.id)
            _casted_value = _type(_value) if _value else _default_value
            _variables[re.escape(var.id)] = repr(_casted_value)
        _pattern = re.compile("|".join(_variables.keys()))
        _value = _pattern.sub(lambda m: _variables[re.escape(m.group(0))], statement)
        return _safe_eval(_value)


    @validator('statement', always=True)
    def statement_validate(cls, statement, values):
        try:
            cls.statement_evaluation(statement, values.get('variables'), defaultdict(int))
        except (SyntaxError, NameError):
            raise ValueError("Invalid syntax")
        return statement
