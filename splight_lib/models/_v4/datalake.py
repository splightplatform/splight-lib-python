from typing import Annotated, Literal

from pydantic import BaseModel, Field

from splight_lib.client.datalake.v4.builder import get_datalake_client
from splight_lib.client.datalake.v4.generic import (
    AggregationFunction,
    Timestamp,
    TimeUnit,
    TransitionSchemaName,
    TransitionSort,
    Value,
)


class DefaultEntryKey(BaseModel):
    asset: str
    attribute: str


class DefaultKeys(BaseModel):
    schema_name: Literal[TransitionSchemaName.DEFAULT]
    entries: list[DefaultEntryKey]

    @classmethod
    def load(cls, entries: list) -> "DefaultKeys":
        return cls(
            schema_name=TransitionSchemaName.DEFAULT,
            entries=entries,
        )


class SolutionEntryKey(BaseModel):
    solution: str
    asset: str
    output: str


class SolutionKeys(BaseModel):
    schema_name: Literal[TransitionSchemaName.SOLUTIONS]
    entries: list[SolutionEntryKey]

    @classmethod
    def load(cls, entries: list) -> "SolutionKeys":
        return cls(
            schema_name=TransitionSchemaName.SOLUTIONS,
            entries=entries,
        )


QueryKeys = Annotated[
    DefaultKeys | SolutionKeys, Field(discriminator="schema_name")
]


class DataReadRequest(BaseModel):
    keys: QueryKeys
    start: Timestamp | None = None
    end: Timestamp | None = None
    time_window_unit: TimeUnit = TimeUnit.SECOND
    time_window_size: int = 1
    aggregation: AggregationFunction = AggregationFunction.MAX
    sort: TransitionSort = TransitionSort.DESC
    limit: int = 1000

    def apply(self) -> dict:
        dl_client = get_datalake_client()
        request = self.model_dump(mode="json")
        response = dl_client.get(request)
        return response["results"]

    async def async_apply(self) -> dict:
        dl_client = get_datalake_client()
        request = self.model_dump(mode="json")
        response = await dl_client.async_get(request)
        return response["results"]


class DefaultDataPoint(DefaultEntryKey):
    value: Value
    timestamp: Timestamp


class DefaultRecords(BaseModel):
    schema_name: Literal[TransitionSchemaName.DEFAULT] = (
        TransitionSchemaName.DEFAULT
    )
    data_points: list[DefaultDataPoint]

    @classmethod
    def load(cls, data_points: list[DefaultDataPoint]) -> "DefaultRecords":
        return cls(
            schema_name=TransitionSchemaName.DEFAULT,
            data_points=data_points,
        )


class SolutionDataPoint(SolutionEntryKey):
    value: Value
    timestamp: Timestamp


class SolutionRecords(BaseModel):
    schema_name: Literal[TransitionSchemaName.SOLUTIONS] = (
        TransitionSchemaName.SOLUTIONS
    )
    data_points: list[SolutionDataPoint]

    @classmethod
    def load(cls, data_points: list[SolutionDataPoint]) -> "SolutionRecords":
        return cls(
            schema_name=TransitionSchemaName.SOLUTIONS,
            data_points=data_points,
        )


WriteRecords = Annotated[
    DefaultRecords | SolutionRecords, Field(discriminator="schema_name")
]


class DataWriteRequest(BaseModel):
    records: WriteRecords

    def apply(self) -> None:
        dl_client = get_datalake_client()
        request = self.model_dump(mode="json")
        dl_client.save(request)

    async def async_apply(self) -> None:
        dl_client = get_datalake_client()
        request = self.model_dump(mode="json")
        await dl_client.async_save(request)
