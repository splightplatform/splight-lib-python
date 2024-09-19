from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Annotated, Any, Generator, Generic, Literal, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from splight_lib.client.datalake import DatalakeClientBuilder
from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.client.datalake.constants import StepName
from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.exceptions import TraceAlreadyExistsError
from splight_lib.settings import settings

MAX_NUM_TRACES = 500
T = TypeVar("T")


def hash(string: str) -> str:
    return sha256(string.encode("utf-8")).hexdigest()


def get_datalake_client() -> AbstractDatalakeClient:
    return DatalakeClientBuilder.build(
        dl_client_type=settings.DL_CLIENT_TYPE,
        parameters={
            "base_url": settings.SPLIGHT_PLATFORM_API_HOST,
            "access_id": settings.SPLIGHT_ACCESS_ID,
            "secret_key": settings.SPLIGHT_SECRET_KEY,
            "buffer_size": settings.DL_BUFFER_SIZE,
            "buffer_timeout": settings.DL_BUFFER_TIMEOUT,
        },
    )


class TraceType(str, Enum):
    QUERY = "QUERY"
    EXPRESSION = "EXPRESSION"
    METADATA = "METADATA"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class PipelineStep(BaseModel):
    name: StepName
    operation: str | dict[str, Any]

    @classmethod
    def from_dict(cls, step_dict: dict[str, Any]) -> Self:
        (name, operation), *aux = step_dict.items()
        return cls(name=name.lstrip("$"), operation=operation)

    def to_step(self) -> dict[str, dict[str, Any]]:
        return {f"${self.name.value}": self.operation}


class Trace(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    ref_id: str
    type: TraceType = TraceType.QUERY
    expression: dict | None = None
    # TODO: Review if it should be list[PipelineStep]
    pipeline: list[dict] = []
    address: Annotated[dict, Field(exclude=True)]

    @classmethod
    def from_address(
        cls, asset: str | Asset, attribute: str | Attribute
    ) -> Self:
        asset_id = asset.id if isinstance(asset, Asset) else asset
        attribute_id = (
            attribute.id if isinstance(attribute, Attribute) else attribute
        )
        return cls(
            ref_id=hash(f"{asset_id}_{attribute_id}"),
            type=TraceType.QUERY,
            pipeline=[
                PipelineStep(
                    name=StepName.MATCH,
                    operation={"asset": asset_id, "attribute": attribute_id},
                ).to_step()
            ],
            address={"asset": asset_id, "attribute": attribute_id},
        )

    def add_step(self, step: PipelineStep) -> None:
        self.pipeline.append(step.to_step())


class DataRequest(Generic[T], BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    collection: str = "default"
    sort_field: str = "timestamp"
    sort_direction: Literal[-1, 1] = -1
    limit: Annotated[int, Field(ge=1, le=10000)] = 10000
    max_time_ms: Annotated[int, Field(ge=1, le=10000)] = 10000
    from_timestamp: datetime | None = None
    to_timestamp: datetime | None = None
    traces: list[Trace] = []

    _dl_client: AbstractDatalakeClient = PrivateAttr()
    _traces_ref: dict[str, dict] = {}

    def add_trace(self, trace: Trace) -> None:
        if trace.ref_id in self._traces_ref:
            raise TraceAlreadyExistsError(trace.ref_id)
        self.traces.append(trace)
        self._traces_ref.update({trace.ref_id: trace.address})

    def as_pipeline(self) -> list[dict[str, Any]]:
        return [step.to_step() for step in self.pipeline]

    def apply(self) -> list[T]:
        dl_client = get_datalake_client()
        request = self.model_dump(mode="json")
        traces = request.pop("traces")
        data = []
        for batch in chunk_list(traces, MAX_NUM_TRACES):
            request["traces"] = batch
            response = dl_client.get(request)
            data.extend(self._parse_respose(response))
        return data

    async def async_apply(self) -> list[T]:
        dl_client = get_datalake_client()
        request = self.model_dump(mode="json")
        data = []
        for batch in chunk_list(self.traces, MAX_NUM_TRACES):
            request["traces"] = batch
            response = await dl_client.async_get(request)
            data.extend(self._parse_respose(response))
        return data

    def _parse_respose(self, response: dict) -> list[T]:
        model_class = self.__orig_class__.__args__[0]
        data = []
        for item in response:
            timestamp = item.pop("timestamp")
            values = [
                model_class(
                    timestamp=timestamp, value=value, **self._traces_ref[key]
                )
                for key, value in item.items()
                if value is not None
            ]
            data.extend(values)
        return data


class DataRecords(BaseModel):
    collection: str = "default"
    records: list[dict[str, Any]] = []

    def apply(self) -> None:
        dl_client = get_datalake_client()
        dl_client.save(self.model_dump(mode="json"))

    async def async_apply(self) -> None:
        dl_client = get_datalake_client()
        await dl_client.async_save(self.model_dump(mode="json"))


def chunk_list(
    datas: list[Any], chunksize: int
) -> Generator[list[Any], None, None]:
    """Split list into chunks

    Parameters
    ----------
    datas : list[Any]
        the list of data
    chunksize : int
        the size of chunk

    Returns
    -------
    Generator with the chunks
    """
    for i in range(0, len(datas), chunksize):
        yield datas[i : i + chunksize]
