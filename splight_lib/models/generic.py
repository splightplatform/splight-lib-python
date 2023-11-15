import ast
from enum import auto
from typing import Union

from strenum import PascalCaseStrEnum

VariableType = Union[str, float, int, bool]


class ValueTypeEnum(PascalCaseStrEnum):
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()


def any_to_float(value) -> float:
    if isinstance(value, (str, bool)):
        new_value = ast.literal_eval(value)
    else:
        int_value = int(value)
        float_value = float(value)
        new_value = int_value if int_value == float_value else float_value
    return new_value


CAST_FUNCTIONS = {
    ValueTypeEnum.NUMBER: any_to_float,
    ValueTypeEnum.STRING: str,
    ValueTypeEnum.BOOLEAN: bool,
}


def cast_value(value: VariableType, value_type: ValueTypeEnum) -> VariableType:
    return CAST_FUNCTIONS[value_type](value)
