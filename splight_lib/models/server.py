import re
from collections import namedtuple
from enum import auto
from typing import Any, NamedTuple

from pydantic import BaseModel, Field, computed_field
from strenum import LowercaseStrEnum, PascalCaseStrEnum

from splight_lib.models.database_base import SplightDatabaseBaseModel
from splight_lib.models.exceptions import (
    InvalidArgument,
    InvalidServerConfigType,
)
from splight_lib.models.file import File
from splight_lib.models.hub_server import HubServer
from splight_lib.models.secret import Secret
from splight_lib.models.variable_types import CUSTOM_TYPES, NATIVE_TYPES

# warnings.filterwarnings("ignore", category=RuntimeWarning)

DATABASE_TYPES = {
    "File": File,
}

DB_MODEL_TYPE_MAPPING = {
    **CUSTOM_TYPES,
    **NATIVE_TYPES,
    **DATABASE_TYPES,
}


def get_field_value(field: dict):
    field_multiple = field.get("multiple", False)
    field_type = field.get("type")
    field_value = field.get("value")

    if not field_value:
        return [] if field_multiple else None

    if field_type in NATIVE_TYPES:
        value = (
            field_value
            if not isinstance(field_value, str)
            else parse_variable_string(field_value)
        )
    elif field.type in CUSTOM_TYPES:
        value = CUSTOM_TYPES.get(field.type).from_string(field.value)
    elif field_type in DATABASE_TYPES:
        model_class = DATABASE_TYPES[field_type]
        value = (
            model_class.retrieve(field_value)
            if not field_multiple
            else [model_class.retrieve(item) for item in field_value]
        )
    return value


def get_model_class(config: BaseModel, name: str) -> NamedTuple:
    config_class = namedtuple(name, [x.name for x in config])
    return config_class


def load_server_config(
    config: list[dict], config_class: NamedTuple
) -> NamedTuple:
    config_dict = {}
    for item in config:
        if item["type"] not in DB_MODEL_TYPE_MAPPING:
            raise InvalidServerConfigType(item["name"], item["type"])
        config_dict.update({item["name"]: get_field_value(item)})
    config = config_class(**config_dict)
    return config


def validate_in_range(value: int, min_value: int, max_value: int) -> None:
    if not (min_value <= value <= max_value):
        raise ValueError(
            f"{value} is out of valid range ({min_value}-{max_value})"
        )


def validate_protocol(protocol: str, valid_protocols: list[str]) -> None:
    if protocol not in valid_protocols:
        raise ValueError(
            f"Protocol {protocol} is not valid. Must be 'tcp' or 'udp'"
        )


def load_server_ports(
    ports: list[dict], model_class: NamedTuple
) -> namedtuple:
    ports_dict = {}
    for port in ports:
        validate_in_range(int(port["internal_port"]), 0, 65535)
        validate_in_range(int(port["exposed_port"]), 0, 65535)
        validate_protocol(port["protocol"], ["tcp", "udp"])
        ports_dict.update({port["name"]: port})
    resources = model_class(**ports_dict)
    return resources


def load_server_env_vars(env_vars: list[dict]) -> namedtuple:
    ntuple = namedtuple("EnvVars", ["name", "value"])
    return [ntuple(**env_var) for env_var in env_vars]


class ServerStatus(PascalCaseStrEnum):
    RUNNING = auto()
    FAILED = auto()
    SUCCEEDED = auto()
    PENDING = auto()
    START_REQUESTED = auto()
    STOP_REQUESTED = auto()
    STOPPED = auto()
    UNKNOWN = auto()


class PrivacyPolicy(LowercaseStrEnum):
    PUBLIC = auto()
    PRIVATE = auto()


class Server(SplightDatabaseBaseModel):
    id: str | None = None
    name: str | None = None
    version: str
    hub_server: HubServer
    raw_config: list[dict] = Field(alias="config")
    raw_ports: list[dict] = Field(alias="ports")
    raw_env_vars: list[dict] = Field(alias="env_vars")

    def model_dump(self, *args, **kwargs):
        kwargs.update({"by_alias": True})
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs):
        kwargs.update({"by_alias": True})
        return super().model_dump_json(*args, **kwargs)

    @computed_field(alias="parsed_config")
    @property
    def config(self) -> NamedTuple:
        model_class = get_model_class(self.hub_server.config, "Config")
        config = load_server_config(self.raw_config, model_class)
        return config

    @computed_field(alias="parsed_ports")
    @property
    def ports(self) -> NamedTuple:
        model_class = get_model_class(self.hub_server.ports, "Ports")
        ports = load_server_ports(self.raw_ports, model_class)
        return ports

    @computed_field(alias="parsed_env_vars")
    @property
    def env_vars(self) -> NamedTuple:
        env_vars = load_server_env_vars(self.raw_env_vars)
        return env_vars

    def update_config(self, **kwargs: dict) -> None:
        valid_params = [x["name"] for x in self.raw_config]
        for key, value in kwargs.items():
            if key not in valid_params:
                raise InvalidArgument(
                    (
                        f"Got invalid parameter {key}. Valid config parameters "
                        f"are {valid_params}"
                    )
                )
            for item in self.raw_config:
                if item["name"] == key:
                    item["value"] = value
                    break

    def update_status(self, status: ServerStatus) -> None:
        _ = self._db_client.operate(
            resource_name="server-status",
            instance={
                "server": self.id,
                "deployment_status": status,
            },
        )


def parse_variable_string(raw_value: str | None) -> Any:
    if raw_value is None:
        return ""
    pattern = re.compile(r"^\$\{\{(\w+)\.(\w+)\}\}$")
    match = pattern.search(raw_value)
    if not match:
        return raw_value
    _, secret_name = match.groups()
    # TODO: handle errors (not found or not allowed)
    secret = Secret.decrypt(name=secret_name)
    return secret.value
