from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field

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
    start: Optional[Timestamp]
    end: Optional[Timestamp] = None
    time_window_unit: TimeUnit = TimeUnit.SECOND
    time_window_size: int = 1
    aggregation: AggregationFunction = AggregationFunction.MAX
    sort: TransitionSort = TransitionSort.DESC
    limit: int = 1000


class DefaultRecord(DefaultEntryKey):
    value: Value
    timestamp: Timestamp


class SolutionRecord(SolutionEntryKey):
    value: Value
    timestamp: Timestamp


class DataWriteRequest(BaseModel):
    schema_name: TransitionSchemaName
    records: list[SolutionRecord] | list[DefaultRecord]
