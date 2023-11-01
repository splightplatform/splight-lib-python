import ast
from enum import auto
from typing import Any, Optional

from pydantic import root_validator
from strenum import PascalCaseStrEnum

from splight_lib.models.base import SplightDatabaseBaseModel


class MetadataType(PascalCaseStrEnum):
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()


class Metadata(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str
    asset: Optional[str]
    type: MetadataType = MetadataType.NUMBER
    value: Optional[Any]

    @root_validator(pre=True)
    def check_value_type(cls, values):
        if values["value"] is None:
            return values

        # TODO: improve the following
        if values["type"] == MetadataType.NUMBER:
            if isinstance(values["value"], str):
                values["value"] = ast.literal_eval(values["value"])
            else:
                _int = int(values["value"])
                _float = float(values["value"])
                values["value"] = _int if _int == _float else _float
        elif values["type"] == MetadataType.BOOLEAN:
            values["value"] = bool(values["value"])
        elif values["type"] == MetadataType.STRING:
            values["value"] = str(values["value"])

        return values
