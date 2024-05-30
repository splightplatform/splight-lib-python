import os
from enum import Enum
from typing import Any, Dict, Tuple, Type

import yaml
from pydantic import ConfigDict
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from splight_lib.constants import DL_BUFFER_SIZE, DL_BUFFER_TIMEOUT

SPLIGHT_HOME = os.path.join(os.path.expanduser("~"), ".splight")


class DatalakeClientType(str, Enum):
    LOCAL = "local"
    SYNC = "sync"
    BUFFERED_SYNC = "buffered_sync"
    BUFFERED_ASYNC = "buffered_async"


class Singleton:
    def __new__(cls, *args, **kw):
        if not hasattr(cls, "_instance"):
            org = super(Singleton, cls)
            cls._instance = org.__new__(cls, *args, **kw)
        return cls._instance


class SplightConfigSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls):
        super().__init__(settings_cls=settings_cls)
        config = {}
        config_file = os.path.join(SPLIGHT_HOME, "config")
        if os.path.exists(config_file):
            with open(config_file) as f:
                config = yaml.safe_load(f)
            if "workspaces" in config:  # splight format config
                workspace = config.get("current_workspace", "default")
                config = config["workspaces"].get(workspace, {})
        self._raw_config = config

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        return (self._raw_config.get(field_name, None), field_name, False)

    def __call__(self) -> Dict[str, Any]:
        values: Dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                values.update({field_key: field_value})
        return values


class SplightSettings(BaseSettings, Singleton):
    SPLIGHT_ACCESS_ID: str = ""
    SPLIGHT_SECRET_KEY: str = ""
    SPLIGHT_PLATFORM_API_HOST: str = "https://api.splight-ai.com"

    # Parameters for the datalake client
    # Review if is better to use another class for only the DL Client settings
    DL_CLIENT_TYPE: DatalakeClientType = DatalakeClientType.BUFFERED_ASYNC
    DL_BUFFER_SIZE: int = DL_BUFFER_SIZE
    DL_BUFFER_TIMEOUT: float = DL_BUFFER_TIMEOUT  # seconds

    model_config = ConfigDict(extra="ignore")

    def configure(self, **params: Dict):
        self.model_validate(params)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        return (
            init_settings,
            env_settings,
            SplightConfigSource(settings_cls=settings_cls),
        )


settings = SplightSettings()
