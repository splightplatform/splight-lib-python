import pandas as pd
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Optional


class Variable(BaseModel):
    args: Dict
    path: Optional[str] = None
    asset_id: Optional[str] = None
    attribute_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# TODO add constraints 
VariableDataFrame = pd.DataFrame