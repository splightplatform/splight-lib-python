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

    @validator('statement', always=True)
    def statement_validate(cls, value, values):
        _value = value
        if values.get('variables'):
            rep = {
                re.escape(val.id): repr(locate(val.type)(1))
                for val in values['variables']
            }
            _pattern = re.compile("|".join(rep.keys()))
            _value = _pattern.sub(lambda m: rep[re.escape(m.group(0))], value)
        try:
            _eval(_value)
        except (SyntaxError, NameError):
            raise ValueError("Invalid syntax")
        return value
