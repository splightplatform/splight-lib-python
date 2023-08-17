from typing import Dict, List

import pandas as pd
from pydantic import BaseModel

from splight_lib.models.native import Boolean, NativeOutput, Number, String


class DataAddresses(BaseModel):
    asset: str
    attribute: str
    type: str

    _type_map = {
        "Number": Number,
        "String": String,
        "Boolean": Boolean,
    }

    def get(self, **params) -> List["NativeOutput"]:
        params["asset"] = self.asset
        params["attribute"] = self.attribute
        return self._type_map[self.type].get(**params)

    def get_dataframe(self, **params) -> pd.DataFrame:
        params["asset"] = self.asset
        params["attribute"] = self.attribute
        return self._type_map[self.type].get_dataframe(**params)

    def save_dataframe(self, dataframe: pd.DataFrame):
        dataframe["asset"] = self.asset
        dataframe["attribute"] = self.attribute
        self._type_map[self.type].save_dataframe(dataframe)
