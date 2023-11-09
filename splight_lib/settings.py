import os
from typing import Any, Dict, Optional, Tuple

import yaml
from pydantic import Extra, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

# from pydantic.env_settings import SettingsSourceCallable

SPLIGHT_HOME = os.path.join(os.path.expanduser("~"), ".splight")


class Singleton:
    def __new__(cls, *args, **kw):
        if not hasattr(cls, "_instance"):
            org = super(Singleton, cls)
            cls._instance = org.__new__(cls, *args, **kw)
        return cls._instance


def yml_config_setting(settings: BaseSettings) -> Dict[str, Any]:
    config = {}
    config_file = os.path.join(SPLIGHT_HOME, "config")
    if os.path.exists(config_file):
        with open(config_file) as f:
            config = yaml.safe_load(f)
        if "workspaces" in config:  # splight format config
            workspace = config.get("current_workspace", "default")
            config = config["workspaces"].get(workspace, {})
    return config


class SplightSettings(BaseSettings, Singleton):
    SPLIGHT_ACCESS_ID: str = ""
    SPLIGHT_SECRET_KEY: str = ""
    SPLIGHT_PLATFORM_API_HOST: str = "https://api.splight-ai.com"
    SPLIGHT_GRPC_HOST: str = "grpc.splight-ai.com:443"

    # Parameters for local environment
    LOCAL_ENVIRONMENT: bool = False
    CURRENT_DIR: Optional[str] = None

    @model_validator(mode="after")
    @classmethod
    def validate_local_environment(
        cls, instance: "SplightSettings"
    ) -> "SplightSettings":
        # local_dev = values.get("LOCAL_ENVIRONMENT")
        if instance.LOCAL_ENVIRONMENT:
            instance.CURRENT_DIR = os.getcwd()
            # values["CURRENT_DIR"] = os.getcwd()
        return instance

    def configure(self, **params: Dict):
        self.parse_obj(params)

    class Config:
        extra = Extra.ignore

        @classmethod
        def customise_sources(
            cls,
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> Tuple[PydanticBaseSettingsSource, ...]:
            return init_settings, yml_config_setting, env_settings


settings = SplightSettings()
