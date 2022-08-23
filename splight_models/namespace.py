from splight_models.base import SplightBaseModel
from pydantic import validator
from typing import Dict


def namespace_transform(raw: str) -> str:
    return raw.lower().replace("_", "")


class Namespace(SplightBaseModel):
    id: str
    environment: Dict = {}
    _extract_id = validator('id', pre=True, allow_reuse=True)(namespace_transform)

