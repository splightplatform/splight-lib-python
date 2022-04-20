import re
import math
from pydantic import BaseModel, validator
from typing import Optional, List, Dict


def _eval(expression):
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


class TriggerVariable(BaseModel):
    id: str
    collection: str = 'default'
    filters: Dict = {}
    key: str = "args.value"
    type: type 


class Trigger(BaseModel):
    id: Optional[str]
    variables: List[TriggerVariable]
    rule: str

    @validator('rule', always=True)
    def rule_validate(cls, value, values):
        _value = value
        if values['variables']:
            rep = {
                re.escape(var.id): str(var.type(1))
                for var in values['variables']
            }
            _pattern = re.compile("|".join(rep.keys()))
            _value = _pattern.sub(lambda m: rep[re.escape(m.group(0))], value)
        try:
            _eval(_value) # Raises on syntax error
        except (SyntaxError, NameError):
            raise ValueError("Invalid syntax")
        return value
