import os
from typing import Any, Dict, Optional, Tuple

import yaml
from pydantic import BaseSettings, Extra, root_validator
from pydantic.env_settings import SettingsSourceCallable

SPLIGHT_HOME = os.path.join(os.getenv("HOME"), ".splight")


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

    # Parameters for local environment
    LOCAL_ENVIRONMENT: bool = False
    CURRENT_DIR: Optional[str]

    @root_validator(allow_reuse=True)
    def validate_local_environment(cls, values: Dict):
        local_dev = values.get("LOCAL_ENVIRONMENT")
        if local_dev:
            values["CURRENT_DIR"] = os.getcwd()
        return values

    def configure(self, **params: Dict):
        self.parse_obj(params)

    class Config:
        extra = Extra.ignore

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, yml_config_setting, env_settings


settings = SplightSettings()
