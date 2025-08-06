from datetime import datetime, timezone
from enum import auto
from itertools import islice
from typing import Any, ClassVar, Generic, Iterable, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator
from strenum import PascalCaseStrEnum, StrEnum

from splight_lib.client.datalake import DatalakeClientBuilder
from splight_lib.client.datalake.common.abstract import AbstractDatalakeClient
from splight_lib.settings import (
    SplightAPIVersion,
    api_settings,
    datalake_settings,
    workspace_settings,
)

T = TypeVar("T")
DataModel = TypeVar("DataModel", bound=BaseModel)
MAX_NUM_RECORDS = 500
MAX_NUM_TRACES = 500


def get_datalake_client(resource: str) -> AbstractDatalakeClient:
    return DatalakeClientBuilder.build(
        version=SplightAPIVersion.V4,
        dl_client_type=datalake_settings.DL_CLIENT_TYPE,
        parameters={
            "resource": resource,
            "base_url": workspace_settings.SPLIGHT_PLATFORM_API_HOST,
            "access_id": workspace_settings.SPLIGHT_ACCESS_ID,
            "secret_key": workspace_settings.SPLIGHT_SECRET_KEY,
            "api_version": api_settings.API_VERSION,
            "buffer_size": datalake_settings.DL_BUFFER_SIZE,
            "buffer_timeout": datalake_settings.DL_BUFFER_TIMEOUT,
        },
    )


def batched(iterable: Iterable, n: int, *, strict: bool = False):
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := list(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError("batched(): incomplete batch")
        yield batch


class DataValueType(PascalCaseStrEnum):
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()


class Aggregation(StrEnum):
    AVG = "mean"
    SUM = "sum"
    MAX = "max"
    MIN = "min"
    COUNT = "count"
    LAST = "last_value"


class GroupByTime(StrEnum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class Sort(StrEnum):
    ASC = "ASC"
    DESC = "DESC"


class AttributeDocument(BaseModel):
    timestamp: datetime = datetime.now(timezone.utc)
    asset: str
    attribute: str
    value: str | int | float | bool

    resource_name: ClassVar[str] = "attributes"


class SolutionOutputDocument(BaseModel):
    timestamp: datetime = datetime.now(timezone.utc)
    asset: str
    solution: str
    output: str
    value: str | int | float | bool

    resource_name: ClassVar[str] = "solutions"


T = TypeVar("T", AttributeDocument, SolutionOutputDocument)


class Records(Generic[T], BaseModel):
    records: list[T] = []

    def apply(self) -> None:
        model_class = self.__orig_class__.__args__[0]
        dl_client = get_datalake_client(model_class.resource_name)
        request = self.model_dump(
            mode="json", exclude={"namespace", "collection"}
        )
        dl_client.save(request)


class Query(Generic[T], BaseModel):
    type: DataValueType = DataValueType.NUMBER
    attributes: str | list[str] | None = None
    outputs: str | list[str] | None = None
    assets: str | list[str] | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    group_by_time: GroupByTime | None = GroupByTime.MINUTE
    aggregation: Aggregation | None = Aggregation.AVG
    sort: Sort | None = Sort.ASC
    limit: int = 10000

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("attributes", "outputs", "assets", mode="before")
    def validate_ids(cls, value: Any) -> list[str]:
        return [value] if isinstance(value, str) else value

    def apply(self) -> list[T]:
        model_class = self.__orig_class__.__args__[0]
        self._validate_model(model_class)
        dl_client = get_datalake_client(model_class.resource_name)
        query = self.model_dump(
            mode="json", exclude_none=True, exclude={"namespace"}
        )
        response = dl_client.get(request=query)["results"]
        return [model_class(**item) for item in response]

    def _validate_model(self, model_class: T):
        if model_class == AttributeDocument:
            if self.outputs or self.assets:
                raise ValueError(
                    (
                        "Outputs and assets cannot be specified for "
                        "AttributeDocument queries."
                    )
                )
        elif model_class == SolutionOutputDocument:
            if self.attributes:
                raise ValueError(
                    (
                        "Attributes cannot be specified for "
                        "SolutionOutputDocument queries."
                    )
                )
        else:
            raise ValueError(
                f"Unsupported model class: {model_class.__name__}"
            )


class DataClient(BaseModel):
    attribute_document: DataModel = AttributeDocument
    solution_output_document: DataModel = SolutionOutputDocument
    records: DataModel = Records
    query: DataModel = Query
