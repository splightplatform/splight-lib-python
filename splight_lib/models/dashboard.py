import json
import re
from enum import auto
from typing import Dict, List, Literal, get_args

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
    hidden: bool | None = None
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
    id: str | None = None
    name: str
    description: str | None = None
    related_assets: List[ResourceSummary] | None = None
    tags: list[ResourceSummary] | None = None


class Tab(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    order: int | None = None
    dashboard: str


class Chart(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    tab: str
    description: str | None = None
    position_x: int | None = None
    position_y: int | None = None
    min_height: int | None = None
    min_width: int | None = None
    display_time_range: bool | None = None
    labels_display: bool | None = None
    labels_aggregation: str | None = None
    labels_placement: str | None = None
    refresh_interval: str | None = None
    relative_window_time: str | None = None
    show_beyond_data: bool | None = None
    timezone: str | None = None
    timestamp_gte: str | None = None
    timestamp_lte: str | None = None
    height: int | None = None
    width: int | None = None
    collection: str | None = None
    chart_items: List[ChartItem] | None = None
    thresholds: List[Threshold] | None = None
    value_mappings: List[
        ExactMatchValueMapping | RangeValueMapping | RegexMatchValueMapping
    ] = []
    timezone: str | None = None

    @classmethod
    def list(cls, **params: Dict):
        db_client = cls._SplightDatabaseBaseModel__get_database_client()

        data = db_client.get(resource_name="chart", **params)

        if cls != Chart:
            data = [
                chart
                for chart in data
                if chart["type"]
                == get_args(cls.model_fields["type"].default)[0]
            ]

        instances = []
        for item in data:
            instance = class_map[item["type"]].model_validate(item)
            instances.append(instance)

        return instances


class DashboardActionListChart(Chart):
    type: str = Literal["actionlist"]
    action_list_type: str
    filter_name: str | None = None
    filter_asset_name: str | None = None


class DashboardAlertEventsChart(Chart):
    type: str = Literal["alertevents"]
    filter_name: str | None = None
    filter_old_status: List[str] | None = None
    filter_new_status: List[str] | None = None


class DashboardAlertListChart(Chart):
    type: str = Literal["alertlist"]
    filter_name: str
    filter_status: List[str]
    alert_list_type: str | None = None


class DashboardAssetListChart(Chart):
    type: str = Literal["assetlist"]
    filter_name: str | None = None
    filter_status: List[str]
    asset_list_type: str | None = None


class DashboardBarChart(Chart):
    type: str = Literal["bar"]
    y_axis_unit: str | None = None
    number_of_decimals: int | None = None
    orientation: str | None = None


class DashboardBarGaugeChart(Chart):
    type: str = Literal["bargauge"]
    max_limit: int | None = None
    number_of_decimals: int | None = None
    orientation: str | None = None


class DashboardCommandListChart(Chart):
    type: str = Literal["commandlist"]
    command_list_type: str
    filter_name: str


class DashboardGaugeChart(Chart):
    type: str = Literal["gauge"]
    max_limit: int | None = None
    number_of_decimals: int | None = None


class DashboardHistogramChart(Chart):
    type: str = Literal["histogram"]
    number_of_decimals: int | None = None
    bucket_count: int
    bucket_size: int | None = None
    histogram_type: str
    sorting: str
    stacked: bool
    categories_top_max_limit: int | None = None


class DashboardImageChart(Chart):
    type: str = Literal["image"]
    image_url: str | None = None
    image_file: str | None = None


class DashboardStatChart(Chart):
    type: str = Literal["stat"]
    y_axis_unit: str | None = None
    border: bool
    number_of_decimals: int | None = None


class DashboardTableChart(Chart):
    type: str = Literal["table"]
    y_axis_unit: str | None = None
    number_of_decimals: int | None = None


class DashboardTextChart(Chart):
    type: str = Literal["text"]
    text: str | None = None


class DashboardTimeseriesChart(Chart):
    type: str = Literal["timeseries"]
    y_axis_max_limit: int | None = None
    y_axis_min_limit: int | None = None
    y_axis_unit: str | None = None
    number_of_decimals: int | None = None
    x_axis_format: str
    x_axis_auto_skip: bool
    x_axis_max_ticks_limit: int | None = None
    line_interpolation_style: str | None = None
    timeseries_type: str | None = None
    fill: bool
    show_line: bool


class_map = {
    "actionlist": DashboardActionListChart,
    "alertevents": DashboardAlertEventsChart,
    "alertlist": DashboardAlertListChart,
    "assetlist": DashboardAssetListChart,
    "bar": DashboardBarChart,
    "bargauge": DashboardBarGaugeChart,
    "commandlist": DashboardCommandListChart,
    "gauge": DashboardGaugeChart,
    "histogram": DashboardHistogramChart,
    "image": DashboardImageChart,
    "stat": DashboardStatChart,
    "table": DashboardTableChart,
    "text": DashboardTextChart,
    "timeseries": DashboardTimeseriesChart,
}
