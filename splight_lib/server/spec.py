import json
from typing import List, Optional, Set, Type

from pydantic import AnyUrl, BaseModel, Field, field_validator

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.server import (
    ConfigParameter,
    Port,
    PrivacyPolicy,
    Server,
    get_field_value,
)
from splight_lib.server.exceptions import DuplicatedValuesError
from splight_lib.utils.custom_model import create_custom_model

VALID_PARAMETER_VALUES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "crontab": str,
    "url": AnyUrl,
    "datetime": None,
    "File": None,  # UUID
}


def check_unique_values(values: List[str]):
    """Checks if there are repeated values in a list of strings.

    Raises
    ------
    DuplicatedValuesError thrown when there is at least two repeated values
    """
    if len(values) != len(set(values)):
        raise DuplicatedValuesError("The list contains duplicated values")


class Spec(BaseModel):
    name: str = Field(pattern=r"^[a-zA-Z0-9\s]+$")
    version: str = Field(pattern=r"^(\d+\.)?(\d+\.)?(\*|\d+)$")
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    privacy_policy: PrivacyPolicy = PrivacyPolicy.PUBLIC
    tags: Set[str] = set()
    config: List[ConfigParameter] = []
    ports: List[Port] = []
    environment: List[str] = []

    @field_validator("config", mode="after")
    def validate_parameters(
        cls, config: List[ConfigParameter]
    ) -> List[ConfigParameter]:
        try:
            check_unique_values([item.name for item in config])
        except DuplicatedValuesError as exc:
            raise ValueError("Repeated Config parameters in spec") from exc

        valid_types_names: List[str] = list(VALID_PARAMETER_VALUES.keys())

        for parameter in config:
            if parameter.type not in valid_types_names:
                raise ValueError(f"Config type {parameter.type} not defined")
        return config

    @field_validator("ports", mode="after")
    def validate_ports(cls, ports: List[Port]) -> List[Port]:
        # Check for unique port names
        port_names = [port.name for port in ports if port.name]
        try:
            check_unique_values(port_names)
        except DuplicatedValuesError as exc:
            raise ValueError("Repeated port names in spec") from exc

        # Check for valid port ranges
        for port in ports:
            if isinstance(port.internal_port, int) and not (
                0 <= port.internal_port <= 65535
            ):
                raise ValueError(
                    f"Internal port {port.internal_port} is out of valid range (0-65535)"
                )
            if isinstance(port.external_port, int) and not (
                0 <= port.external_port <= 65535
            ):
                raise ValueError(
                    f"External port {port.external_port} is out of valid range (0-65535)"
                )

        return ports

    @classmethod
    def from_file(cls, file_path: str) -> "Spec":
        with open(file_path, "r") as fid:
            data = json.load(fid)
        return cls.model_validate(data)

    def get_config_model(self) -> Type[BaseModel]:
        """Creates a BaseModel class that represents the component's config.

        Returns
        -------
        Type[BaseModel] the class object for the config.
        """
        model = create_custom_model(
            model_name="Input",
            parameters=self.config,
            config_dict={"use_enum_values": True},
        )
        return model

    def server_config(self, server_id: str) -> BaseModel:
        """Creates the config for the server given the id. The parameters
        values are retrieved from the database.

        Parameters
        ----------
        server_id: str
            The servers

        Returns
        -------
        BaseModel: The server's config.
        """
        input_model = self.get_config_model()
        server = Server.retrieve(server_id)
        values = {
            param.name: get_field_value(param) for param in server.config
        }
        return input_model.model_validate(values)
