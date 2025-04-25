from typing import Annotated

from pydantic import BaseModel, Field

from splight_lib.models._v4.component import InputParameter
from splight_lib.models.database import PrivacyPolicy, SplightDatabaseBaseModel


class Port(BaseModel):
    name: str | None = None
    protocol: str = "tcp"
    internal_port: int
    exposed_port: int


class HubServer(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    version: str
    description: str | None = None
    tags: Annotated[list[str] | None, Field()] = []
    privacy_policy: PrivacyPolicy = PrivacyPolicy.PUBLIC

    config: list[InputParameter] = []
    ports: list[Port] = []
    environment: list[dict[str, str]] = []
