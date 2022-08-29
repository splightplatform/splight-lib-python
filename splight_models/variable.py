import pandas as pd
<<<<<<< HEAD
from typing import Dict, Optional
from .datalake import DatalakeModel
=======
from pydantic import Field
from typing import Dict, Union, Optional
from .asset import Asset
from .attribute import Attribute
from .datalake import DatalakeModel, RunnerDatalakeModel
>>>>>>> 2877884 (Update datalake and abstract component)


class Variable(DatalakeModel):
    args: Optional[Dict] = None
    path: Optional[str] = None
    asset_id: Optional[str] = None
    attribute_id: Optional[str] = None


class ConnectorOutput(RunnerDatalakeModel):
    asset: Union[Asset, str]
    attribute: Union[Attribute, str]


class FloatValue(ConnectorOutput):
    output_format: str = Field("FloatValue", const=True)
    value: float


class StrValue(ConnectorOutput):
    output_format: str = Field("StrValue", const=True)
    value: str


class BoolValue(ConnectorOutput):
    output_format: str = Field("BoolValue", const=True)
    value: bool


class VariableDataFrame(pd.DataFrame):
    pass
