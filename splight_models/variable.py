import pandas as pd
from typing import Dict, Optional
from .datalake import DatalakeModel


class Variable(DatalakeModel):
    args: Optional[Dict] = None
    path: Optional[str] = None
    asset_id: Optional[str] = None
    attribute_id: Optional[str] = None


class VariableDataFrame(pd.DataFrame):
    pass
