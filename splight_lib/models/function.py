import json
import re
from enum import auto
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    ValidationError,
    model_validator,
)
from strenum import LowercaseStrEnum, UppercaseStrEnum
from typing_extensions import TypedDict

from splight_lib.models.database_base import (
    ResourceSummary,
    SplightDatabaseBaseModel,
)
from splight_lib.models.exceptions import (
    InvalidFunctionConfiguration,
    MissingFunctionItemExpression,
)
from splight_lib.models.generic import ValueTypeEnum


class FunctionItemType(UppercaseStrEnum):
    EXPRESSION = auto()
    QUERY = auto()
    METADATA = auto()


class QueryFilter(TypedDict):
    id: str
    name: str


class TypedQueryFilter(TypedDict):
    id: str
    name: str
    type: ValueTypeEnum


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

    id: Annotated[str | None, Field(None, max_length=100)]

    ref_id: Annotated[str, Field(max_length=5)]
    type: FunctionItemType = FunctionItemType.QUERY

    expression: str | None = ""
    expression_plain: str | None = ""

    query_filter_asset: QueryFilter | None = None
    query_filter_attribute: TypedQueryFilter | None = None

    query_group_function: GroupCriteria | None = GroupCriteria.EMPTY
    query_group_unit: GroupUnit | None = GroupUnit.EMPTY

    query_sort_field: str | None = ""
    query_sort_direction: Annotated[int, Field(-1, ge=-1, le=1)]

    query_plain: str | None = ""

    @model_validator(mode="after")
    def validate_expression(self):
        if self.type == FunctionItemType.EXPRESSION:
            if self.expression is None:
                raise MissingFunctionItemExpression(
                    "Parameter 'expression' is required for expression type function items"
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
            for attr in [
                ("query_filter_asset", self.query_filter_asset),
                ("query_filter_attribute", self.query_filter_attribute),
            ]:
                if attr is None:
                    raise ValidationError(
                        (
                            f"Parameter '{attr}' is required for query type "
                            "functions items"
                        )
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
    id: Annotated[str | None, Field(None, max_length=100)]
    name: str
    description: str | None = None

    tags: list[ResourceSummary] | None = None
    active: bool = True
    time_window: int = 5 * 60
    function_items: list[FunctionItem] = []

    type: Literal["cron", "rate"]
    target_variable: str
    target_asset: QueryFilter  # NOTE: optional in API
    target_attribute: TypedQueryFilter  # NOTE: optional in API

    cron_minutes: str | None = None
    cron_hours: str | None = None
    cron_dom: str | None = None
    cron_month: str | None = None
    cron_dow: str | None = None
    cron_year: str | None = None

    rate_value: PositiveInt | None = None
    rate_unit: Literal["day", "hour", "minute"] | None = None

    @model_validator(mode="after")
    def validate_type(self):
        if self.type == "cron":
            for attr, value in [
                ("cron_year", self.cron_year),
                ("cron_moth", self.cron_month),
                ("cron_hour", self.cron_hours),
                ("cron_minutes", self.cron_minutes),
                ("cron_dow", self.cron_dow),
                ("cron_dom", self.cron_dom),
            ]:
                if value is None:
                    raise InvalidFunctionConfiguration(
                        (
                            f"Parameter {attr} is required for '{self.type}' "
                            "type functions"
                        )
                    )
        if self.type == "rate":
            for attr in [
                ("rate_value", self.rate_value),
                ("rate_unit", self.rate_unit),
            ]:
                if attr is None:
                    raise InvalidFunctionConfiguration(
                        (
                            f"Parameter {attr} is required for '{self.type}' "
                            "type functions"
                        )
                    )

        return self
