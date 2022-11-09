import builtins
import operator
from splight_models.base import SplightBaseModel
from enum import Enum
from pydantic import validator
from typing import Any, Optional, Dict
from splight_models.constants import SeverityType
from splight_models.datalake import DatalakeOutputQuery

GREATER_THAN = 'gt'
GREATER_THAN_OR_EQUAL = 'ge'
LOWER_THAN = 'lt'
LOWER_THAN_OR_EQUAL = 'le'
EQUAL = 'eq'

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

class OperatorType(str, Enum):
    greater_than = GREATER_THAN
    greater_than_or_equal = GREATER_THAN_OR_EQUAL
    lower_than = LOWER_THAN
    lower_than_or_equal = LOWER_THAN_OR_EQUAL
    equal = EQUAL

class Rule(SplightBaseModel):
    id: Optional[str]
    query: DatalakeOutputQuery
    value: str
    type: RuleVariableType = RuleVariableType.str
    message: str
    name: Optional[str]
    description: Optional[str] = None
    severity: SeverityType = SeverityType.info
    operator: OperatorType = OperatorType.equal
    period: float = 1

    @validator("name", always=True)
    def get_name(cls, name: str, values: Dict[str, Any]) -> str:
        if not name:
            return values.get('message', "Rule")
        return name

    @validator("description", always=True)
    def get_description(cls, description: str, values: Dict[str, Any]) -> str:
        if not description:
            return values.get('value', None)
        return description

    def is_satisfied(self, value):
        rule_value = getattr(builtins, self.type)(self.value)
        value = getattr(builtins, self.type)(value)
        return getattr(operator, self.operator)(value, rule_value)
