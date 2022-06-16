import pandas as pd
from datetime import datetime, timezone
from pydantic import Field
from typing import Dict, Optional
from .base import SplightBaseModel


class Variable(SplightBaseModel):
    args: Optional[Dict] = None
    path: Optional[str] = None
    asset_id: Optional[str] = None
    attribute_id: Optional[str] = None
    instance_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VariableDataFrame(pd.DataFrame):
    def fold(self, asset_id: str, key: str, freq: str = "H", aggregation: str = "mean") -> pd.DataFrame:
        _df = self.copy()
        if _df.empty:
            return _df
        _df = _df[_df["asset_id"] == asset_id]
        _df.timestamp = _df.timestamp.dt.round(freq=freq)
        _df = _df.pivot_table(values=key, index=_df.timestamp, columns='attribute_id', aggfunc=aggregation)
        return _df

    @classmethod
    def unfold(cls, df: pd.DataFrame, asset_id: str, key: str = "value"):
        _df = df.copy()
        if _df.empty:
            return cls(_df)
        _df = pd.melt(_df.reset_index(), id_vars="timestamp").dropna()
        _df = _df.rename(columns={"value": key})
        _df.insert(1, "asset_id", asset_id)
        _df = _df.rename(columns={"variable": "attribute_id"})
        return cls(_df)
