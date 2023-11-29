import json
import re
from enum import auto
from typing import List, Literal, Optional

from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    ValidationError,
    model_validator,
)
from strenum import LowercaseStrEnum, UppercaseStrEnum
from typing_extensions import TypedDict

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.base import SplightDatabaseBaseModel


class FunctionItemType(UppercaseStrEnum):
    EXPRESSION = auto()
    QUERY = auto()


class QueryFilter(TypedDict):
    id: str
    name: str


class GroupUnit(LowercaseStrEnum):
    SECOND = auto()
    MINUTE = auto()
    HOUR = auto()
    DAY = auto()
    MONTH = auto()


class GroupCriteria(LowercaseStrEnum):
    EMPTY = ""
    AVG = auto()
    SUM = auto()
    MIN = auto()
    MAX = auto()
    LAST = auto()


class FunctionItem(BaseModel):
    id: Optional[str] = Field(None, max_length=100)
    ref_id: str
    type: FunctionItemType = FunctionItemType.QUERY
    expression: str = ""
    query_filter_asset: Optional[QueryFilter] = None
    query_filter_attribute: Optional[QueryFilter] = None
    expression_plain: Optional[str] = None
    query_group_unit: Optional[GroupUnit] = None
    query_group_function: Optional[GroupCriteria] = None
    query_sort_field: Optional[str] = None
    query_sort_direction: Optional[int] = None
    query_plain: Optional[str] = None

    @model_validator(mode="after")
    def validate_expression(self):
        if self.expression:
            if self.type != FunctionItemType.EXPRESSION:
                raise ValidationError(
                    "type must be EXPRESSION if a expression is passed."
                )
            self.expression_plain = (
                self._get_expression_plain()
                if self.expression_plain is None
                else self.expression_plain
            )
        return self

    @model_validator(mode="after")
    def validate_query(self):
        if self.query_filter_asset is not None:
            if self.type != FunctionItemType.QUERY:
                raise ValidationError(
                    "type must be QUERY if a query_filter_asset is passed."
                )
            self.query_plain = (
                self._get_query_plain()
                if self.query_plain is None
                else self.query_plain
            )
        return self

    def _get_expression_plain(self):
        pattern = r"\$\w+"
        args = re.findall(pattern, self.expression)
        str_args = ", ".join(args)
        body = f"function ({str_args}) {{ return {self.expression} }}"
        expression_plain = {
            "$function": {"body": body, "args": args, "lang": "js"}
        }
        return json.dumps(expression_plain)

    def _get_query_plain(self):
        query_plain = [
            {
                "$match": {
                    "asset": self.query_filter_asset["id"],
                    "attribute": self.query_filter_attribute["id"],
                }
            }
        ]
        return json.dumps(query_plain)


class Function(SplightDatabaseBaseModel):
    id: Optional[str] = Field(None, max_length=100)
    name: str
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )

    active: bool = True
    time_window: int = 5 * 60
    function_items: List[FunctionItem] = []

    type: Literal["cron", "rate"]
    target_variable: str
    target_asset: Optional[QueryFilter] = None
    target_attribute: Optional[QueryFilter] = None

    cron_minutes: Optional[str] = None
    cron_hours: Optional[str] = None
    cron_dom: Optional[str] = None
    cron_month: Optional[str] = None
    cron_dow: Optional[str] = None
    cron_year: Optional[str] = None

    rate_value: Optional[PositiveInt] = None
    rate_unit: Optional[Literal["day", "hour", "minute"]] = None
