import re
import warnings
from collections import namedtuple
from datetime import datetime
from enum import auto
from typing import Any, NamedTuple, Optional

from pydantic import AnyUrl, BaseModel, Field, computed_field
from strenum import LowercaseStrEnum, PascalCaseStrEnum

from splight_lib.models.database_base import SplightDatabaseBaseModel
from splight_lib.models.exceptions import (
    InvalidArgument,
    InvalidServerConfigType,
)
from splight_lib.models.file import File
from splight_lib.models.hub_server import HubServer
from splight_lib.models.secret import Secret

warnings.filterwarnings("ignore", category=RuntimeWarning)

NATIVE_TYPES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "datetime": datetime,
    "url": AnyUrl,
}

DATABASE_TYPES = {
    "File": File,
}

DB_MODEL_TYPE_MAPPING = {
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


def load_server_ports(
    ports: list[dict], model_class: NamedTuple
) -> namedtuple:
    ports_dict = {}
    for port in ports:
        if isinstance(port["internal_port"], int) and not (
            0 <= port["internal_port"] <= 65535
        ):
            raise ValueError(
                f"Internal port {port['internal_port']} is out of valid range (0-65535)"
            )
        if isinstance(port["exposed_port"], int) and not (
            0 <= port["exposed_port"] <= 65535
        ):
            raise ValueError(
                f"External port {port['exposed_port']} is out of valid range (0-65535)"
            )
        if port["protocol"] not in ["tcp", "udp"]:
            raise ValueError(
                f"Protocol {port['protocol']} is not valid. Must be 'tcp' or 'udp'"
            )
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


class Port(BaseModel):
    name: Optional[str]
    protocol: str
    internal_port: int
    exposed_port: int


class Server(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
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

    def update_config(self, **kwargs: dict):
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

    def update_status(self, status: ServerStatus):
        _ = self._db_client.operate(
            resource_name="server-status",
            instance={
                "server": self.id,
                "deployment_status": status,
            },
        )


def parse_variable_string(raw_value: Optional[str]) -> Any:
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
