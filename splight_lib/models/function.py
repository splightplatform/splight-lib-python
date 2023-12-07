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
    EMPTY = ""
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
    # NOTE: the defaults are inconsistent because
    # we never made a clear contract between the lib, api and frontend

    id: Optional[str] = Field(None, max_length=100)

    ref_id: str
    type: FunctionItemType = FunctionItemType.QUERY

    expression: str = ""
    expression_plain: str = ""

    query_filter_asset: Optional[QueryFilter] = None
    query_filter_attribute: Optional[QueryFilter] = None

    query_group_function: GroupCriteria = GroupCriteria.EMPTY
    query_group_unit: GroupUnit = GroupUnit.EMPTY

    query_sort_field: str = ""
    query_sort_direction: int = -1

    # NOTE: why is this None as default but not "" like 'expression_plain'
    query_plain: Optional[str] = None

    @model_validator(mode="after")
    def validate_expression(self):
        if self.type == FunctionItemType.EXPRESSION:
            if self.expression is None:
                raise ValidationError(
                    f"Parameter 'expression' is required for expression type function items"
                )
            self.expression_plain = (
                self._get_expression_plain()
                if self.expression_plain is None
                else self.expression_plain
            )
        return self

    @model_validator(mode="after")
    def validate_query(self):
        if self.type == FunctionItemType.QUERY:
            for attr in [self.query_filter_asset, self.query_filter_attribute]:
                if attr is None:
                    raise ValidationError(
                        f"Parameter '{attr}' is required for query type functions items"
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
            },
        ]
        # NOTE: The frontend only sets the rest of the query
        # if both group_unit and group_function are set
        if self.query_group_unit and self.query_group_function:
            query_plain.extend(
                [
                    {
                        "$addFields": {
                            "timestamp": {
                                "$dateTrunc": {
                                    "date": "$timestamp",
                                    "unit": self.query_group_unit,
                                    "binSize": 1,
                                }
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$timestamp",
                            "value": {
                                f"${self.query_group_function}": "$value"
                            },
                            "timestamp": {"$last": "$timestamp"},
                        }
                    },
                ]
            )
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
    target_asset: QueryFilter  # NOTE: optional in API
    target_attribute: QueryFilter  # NOTE: optional in API

    cron_minutes: Optional[str] = None
    cron_hours: Optional[str] = None
    cron_dom: Optional[str] = None
    cron_month: Optional[str] = None
    cron_dow: Optional[str] = None
    cron_year: Optional[str] = None

    rate_value: Optional[PositiveInt] = None
    rate_unit: Optional[Literal["day", "hour", "minute"]] = None

    @model_validator(mode="after")
    def validate_type(self):
        if self.type == "cron":
            for attr in [
                self.cron_year,
                self.cron_month,
                self.cron_hours,
                self.cron_minutes,
                self.cron_dow,
                self.cron_dom,
            ]:
                if attr is None:
                    raise ValidationError(
                        f"Parameter {attr} is required for '{self.type}' type functions"
                    )
        if self.type == "rate":
            for attr in [self.rate_value, self.rate_unit]:
                if attr is None:
                    raise ValidationError(
                        f"Parameter {attr} is required for '{self.type}' type functions"
                    )

        return self
