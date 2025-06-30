from splight_lib.models._v4.base import AttributeType, ValueType
from splight_lib.models._v4.exceptions import InvalidOperation
from splight_lib.models.database import SplightDatabaseBaseModel


class Attribute(SplightDatabaseBaseModel):
    id: str | None = None
    asset: str | None = None
    name: str
    description: str | None = None
    type: ValueType
    unit: str | None = None
    origin: AttributeType

    def save(self) -> None:
        raise InvalidOperation("save")

    def delete(self) -> None:
        raise InvalidOperation("delete")
