# TODO rename this file or move it to datalake
import pandas as pd
from pydantic import Field
from typing import Dict, Union, Optional
from .asset import Asset
from .attribute import Attribute
from .datalake import DatalakeModel, DatalakeModel

# TODO remove Variable and VariableDataFrame
class Variable(DatalakeModel):
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None
    args: Optional[Dict] = None
    path: Optional[str] = None
    asset_id: Optional[str] = None
    attribute_id: Optional[str] = None


class VariableDataFrame(pd.DataFrame):
    pass

# TODO rename ConnectorOutput to AssetAttributeDatalakeModel
# furthermore. does it make sense to have this metamodel?
class ConnectorOutput(DatalakeModel):
    asset: Union[Asset, str]
    attribute: Union[Attribute, str]


class Number(ConnectorOutput):
    output_format: str = Field("Number", const=True)
    value: float

    class Meta:
        collection_name = "Splight.Number"


class String(ConnectorOutput):
    output_format: str = Field("String", const=True)
    value: str

    class Meta:
        collection_name = "Splight.String"


class Boolean(ConnectorOutput):
    output_format: str = Field("Boolean", const=True)
    value: bool

    class Meta:
        collection_name = "Splight.Boolean"
