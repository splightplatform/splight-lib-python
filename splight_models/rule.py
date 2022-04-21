import re
import json
json.dumps
import math
from enum import Enum
from pydoc import locate
from pydantic import BaseModel, validator
from typing import Optional, List, Dict


def _eval(expression):
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
    id: Optional[str]
    collection: str = 'default'
    filters: Dict = {}
    key: str = "args.value"
    type: RuleVariableType = RuleVariableType.str


class Rule(BaseModel):
    id: Optional[str]
    variables: List[RuleVariable]
    statement: str

    @validator('statement', always=True)
    def statement_validate(cls, value, values):
        _value = value
        if values['variables']:
            rep = {
                re.escape(var.id): repr(locate(var.type)(1))
                for var in values['variables']
            }
            _pattern = re.compile("|".join(rep.keys()))
            _value = _pattern.sub(lambda m: rep[re.escape(m.group(0))], value)
        try:
            _eval(_value)
        except (SyntaxError, NameError):
            raise ValueError("Invalid syntax")
        return value
