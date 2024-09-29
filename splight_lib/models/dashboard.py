# TODO: set types fixed values
import json
import re
from enum import auto

from pydantic import BaseModel, ValidationError, model_validator
from strenum import UppercaseStrEnum

from splight_lib.models.alert import AlertItemType
from splight_lib.models.database_base import (
    ResourceSummary,
    SplightDatabaseBaseModel,
)
from splight_lib.models.exceptions import MissingAlertItemExpression


class ChartItemType(UppercaseStrEnum):
    QUERY = auto()
    EXPRESSION = auto()


class Threshold(BaseModel):
    color: str | None = None
    display_text: str | None = None
    value: float | None = None


class ValueMapping(BaseModel):
    display_text: str | None = None
    order: int = 0


class ExactMatchValueMapping(ValueMapping):
    match_value: str | None = None


class RangeValueMapping(ValueMapping):
    range_start: float | None = None
    range_end: float | None = None


class RegexMatchValueMapping(ValueMapping):
    regular_expression: str | None = None


class Filter(SplightDatabaseBaseModel):
    id: str | None = None
    chart_item: str
    operator: str | None = None
    key: str | None = None
    value: str | None = None
    label: str | None = None


class AdvancedFilter(SplightDatabaseBaseModel):
    id: str | None = None
    chart_item: str
    operator: str | None = None
    key: str | None = None
    field: str | None = None
    value: str | None = None


class ChartItem(BaseModel):
    color: str | None = None
    ref_id: str
    type: ChartItemType = ChartItemType.QUERY
    label: str
    hidden: bool = False
    expression: str | None = None
    expression_plain: str | None = None
    query_filter_asset: ResourceSummary | None = None
    query_filter_attribute: ResourceSummary | None = None
    query_plain: str = ""
    query_group_unit: str | None = None
    query_group_function: str | None = None
    query_sort_direction: int | None = -1
    query_limit: int = 10000

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


class Dashboard(SplightDatabaseBaseModel):
    id: str | None
    name: str
    description: str | None
    related_assets: list(ResourceSummary)
    tags: list(ResourceSummary)


class Tab(SplightDatabaseBaseModel):
    id: str | None
    name: str
    order: int | None
    dashboard: str


class Chart(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    tab: str
    description: str | None
    position_x: int | None
    position_y: int | None
    min_height: int | None
    min_width: int | None
    display_time_range: bool
    labels_display: bool
    labels_aggregation: str
    labels_placement: str
    refresh_interval: str
    relative_window_time: str
    show_beyond_data: bool
    timezone: str
    timestamp_gte: str
    timestamp_lte: str
    height: int
    width: int
    collection: str
    chart_items: list[ChartItem]
    thresholds: list[Threshold]
    value_mappings: list[
        ExactMatchValueMapping | RangeValueMapping | RegexMatchValueMapping
    ] = []


class DashboardActionListChart(Chart):
    type: str = "actionlist"
    action_list_type: str
    filter_name: str
    filter_asset_name: str | None


class DashboardAlertEventsChart(Chart):
    type: str = "alertevents"
    filter_name: str
    filter_old_status: str
    filter_new_status: str


class DashboardAlertListChart(Chart):
    type: str = "alertlist"
    filter_name: str
    filter_status: list(str)
    alert_list_type: str | None


class DashboardAssetListChart(Chart):
    type: str = "assetlist"
    filter_name: str
    filter_status: list(str)
    asset_list_type: str | None


class DashboardBarChart(Chart):
    type: str = "bar"
    y_axis_unit: str | None
    number_of_decimals: int | None
    orientation: int | None


class DashboardBarGaugeChart(Chart):
    type: str = "bargauge"
    max_limit: int | None
    number_of_decimals: int | None
    orientation: str | None


class DashboardCommandListChart(Chart):
    type: str = "commandlist"
    command_list_type: str
    filter_name: str


class DashboardGaugeChart(Chart):
    type: str = "gauge"
    max_limit: int | None
    number_of_decimals: int | None


class DashboardHistogramChart(Chart):
    type: str = "histogram"
    number_of_decimals: int | None
    bucket_count: int
    bucket_size: int
    histogram_type: str
    sorting: str
    stacked: bool
    categories_top_max_limit: int | None


class DashboardImageChart(Chart):
    type: str = "image"
    image_url: str | None
    image_file: str | None


class DashboardStatChart(Chart):
    type: str = "stat"
    y_axis_unit: str
    border: bool
    number_of_decimals: int | None


class DashboardTableChart(Chart):
    type: str = "table"
    y_axis_unit: str
    number_of_decimals: int


class DashboardTextChart(Chart):
    type: str = "text"
    text: str | None


class DashboardTimeseriesChart(Chart):
    type: str = "timeseries"
    y_axis_max_limit: int | None
    y_axis_min_limit: int | None
    y_axis_unit: str | None
    number_of_decimals: int | None
    x_axis_format: str
    x_axis_auto_skip: bool
    x_axis_max_ticks_limit: int | None
    line_interpolation_style: str | None
    timeseries_type: str | None
    fill: bool
    show_line: bool
