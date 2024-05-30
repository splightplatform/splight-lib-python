from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel, PrivateAttr, validator

from splight_lib.client.datalake import DatalakeClientBuilder
from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.settings import settings
from splight_lib.stringcase import camelcase


def get_datalake_client() -> AbstractDatalakeClient:
    client = DatalakeClientBuilder.build(
        dl_client_type=settings.DL_CLIENT_TYPE,
        parameters={
            "base_url": settings.SPLIGHT_PLATFORM_API_HOST,
            "access_id": settings.SPLIGHT_ACCESS_ID,
            "secret_key": settings.SPLIGHT_SECRET_KEY,
        },
    )
    return client


def dict_to_pipeline(value: Dict) -> Dict:
    return {k: convert_to_pipeline(v) for k, v in value.items()}


def list_to_pipeline(value: List) -> List[Dict]:
    return [convert_to_pipeline(item) for item in value]


def convert_to_pipeline(value: Any) -> Dict:
    if isinstance(value, dict):
        pipeline = dict_to_pipeline(value)
    elif isinstance(value, list):
        pipeline = list_to_pipeline(value)
    elif isinstance(value, (str, float, int)):
        pipeline = value
    else:
        pipeline = value.as_pipeline()
    return pipeline


class Operation(BaseModel):
    operator: str  # TODO: Use enum?
    value: Any

    @validator("operator")
    def add_prefix(cls, op: str):
        op = camelcase(op)
        return op if op.startswith("$") else f"${op}"

    def as_pipeline(self) -> Dict:
        return {self.operator: convert_to_pipeline(self.value)}


class DataPipeline(BaseModel):
    operations: List[Operation] = []
    from_timestamp: datetime
    to_timestamp: Optional[datetime] = None
    _client: AbstractDatalakeClient = PrivateAttr()

    def __init__(self, **parameters):
        super().__init__(**parameters)
        self._client = get_datalake_client()

    @property
    def raw(self) -> List[Dict]:
        return [x.as_pipeline() for x in self.operations]

    def execute(self) -> pd.DataFrame:
        return self._client.execute_query(
            from_timestamp=self.from_timestamp,
            to_timestamp=self.to_timestamp,
            query=self.raw,
        )

    def add_operation(self, operation: Operation):
        self.operations.append(operation)
