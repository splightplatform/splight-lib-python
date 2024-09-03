import json
import re
from enum import Enum, auto
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
from splight_lib.models.database_base import SplightDatabaseBaseModel
from splight_lib.models.exceptions import (
    InvalidAlertConfiguration,
    MissingAlertItemExpression,
)


class AlertItemType(UppercaseStrEnum):
    EXPRESSION = auto()
    QUERY = auto()


class QueryFilter(TypedDict):
    id: str
    name: str


class GroupUnit(LowercaseStrEnum):
    EMPTY = ""
    MINUTE = auto()
    HOUR = auto()
    DAY = auto()


class GroupCriteria(LowercaseStrEnum):
    EMPTY = ""
    AVG = auto()
    SUM = auto()
    MIN = auto()
    MAX = auto()
    LAST = auto()


class AlertItem(BaseModel):
    id: Optional[str] = Field(None, max_length=100)

    ref_id: str = Field(max_length=5)
    type: AlertItemType = AlertItemType.QUERY
    label: Optional[str] = None

    expression: Optional[str] = None
    expression_plain: Optional[str] = ""

    query_filter_asset: Optional[QueryFilter] = None
    query_filter_attribute: Optional[QueryFilter] = None
    query_filter_metadata: Optional[QueryFilter] = None

    query_group_function: Optional[GroupCriteria] = None
    query_group_unit: Optional[GroupUnit] = None

    query_sort_field: Optional[str] = None
    query_sort_direction: Optional[int] = Field(-1, ge=-1, le=1)

    query_plain: Optional[str] = ""
    query_limit: int = Field(10000, ge=1, le=10000)

    @model_validator(mode="after")
    def validate_expression(self):
        if self.type == AlertItemType.EXPRESSION:
            if self.expression is None:
                raise MissingAlertItemExpression(
                    "Parameter 'expression' is required for expression type alert items"
                )
            self.expression_plain = (
                self._get_expression_plain()
                if self.expression_plain is None
                else self.expression_plain
            )
        return self

    @model_validator(mode="after")
    def validate_query(self):
        if self.type == AlertItemType.QUERY:
            for attr in [
                ("query_filter_asset", self.query_filter_asset),
                ("query_filter_attribute", self.query_filter_attribute),
            ]:
                if attr is None:
                    raise ValidationError(
                        (
                            f"Parameter '{attr}' is required for query type "
                            "alert items"
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


class AlertStatus(LowercaseStrEnum):
    ALERT = auto()
    NO_ALERT = auto()
    NO_DATA = auto()
    TIMEOUT = auto()
    DISABLED = auto()
    ERROR = auto()
    WARNING = auto()


class AlertType(LowercaseStrEnum):
    CRON = auto()
    RATE = auto()


class StatementOperator(str, Enum):
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "ge"
    LOWER_THAN = "lt"
    LOWER_THAN_OR_EQUAL = "le"
    EQUAL = "eq"


class ThresholdStatus(LowercaseStrEnum):
    ALERT = auto()
    WARNING = auto()
    NO_ALERT = auto()


class AlertSeverity(LowercaseStrEnum):
    SEV1 = auto()
    SEV2 = auto()
    SEV3 = auto()
    SEV4 = auto()
    SEV5 = auto()
    SEV6 = auto()
    SEV7 = auto()
    SEV8 = auto()


class AlertThreshold(BaseModel):
    value: float
    status: ThresholdStatus
    status_text: Optional[str]


class StatementAggregation(LowercaseStrEnum):
    AVG = auto()
    LAST = auto()
    MAX = auto()
    MIN = auto()
    SUM = auto()


class Alert(SplightDatabaseBaseModel):
    id: Optional[str] = Field(None, max_length=100)
    name: str
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )

    assets: List[QueryFilter] = []
    alert_items: List[AlertItem] = []
    destinations_list: List[str] = []

    type: AlertType

    active: bool = True
    status: AlertStatus = AlertStatus.NO_ALERT
    status_text: Optional[str] = Field(default=None, max_length=400)

    stmt_time_window: int
    stmt_target_variable: Optional[str] = Field(default=None, max_length=5)
    stmt_operator: StatementOperator
    stmt_aggregation: StatementAggregation
    stmt_thresholds: List[AlertThreshold]

    notify_no_data: bool = True
    notify_error: bool = True
    notify_timeout: bool = True
    custom_message: Optional[str] = Field(default=None, max_length=200)

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
            for attr, value in [
                ("cron_year", self.cron_year),
                ("cron_moth", self.cron_month),
                ("cron_hour", self.cron_hours),
                ("cron_minutes", self.cron_minutes),
                ("cron_dow", self.cron_dow),
                ("cron_dom", self.cron_dom),
            ]:
                if value is None:
                    raise InvalidAlertConfiguration(
                        (
                            f"Parameter {attr} is required for '{self.type}' "
                            "type alerts"
                        )
                    )
        if self.type == "rate":
            for attr in [
                ("rate_value", self.rate_value),
                ("rate_unit", self.rate_unit),
            ]:
                if attr is None:
                    raise InvalidAlertConfiguration(
                        (
                            f"Parameter {attr} is required for '{self.type}' "
                            "type alerts"
                        )
                    )

        return self
