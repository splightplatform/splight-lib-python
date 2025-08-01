from enum import Enum
from typing import Any

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from .config import (
    SplightConfigError,
    SplightConfigManager,
    Workspace,
    WorkspaceNotFoundError,
)


class SplightAPIVersion(str, Enum):
    V3 = "v3"
    V4 = "v4"

    def __str__(self) -> str:
        return self.value


class Singleton:
    def __new__(cls, *args, **kw):
        if not hasattr(cls, "_instance"):
            org = super(Singleton, cls)
            cls._instance = org.__new__(cls, *args, **kw)
        return cls._instance


class WorkspaceConfigSource(PydanticBaseSettingsSource):
    def __call__(self) -> dict[str, Any]:
        self.wm = SplightConfigManager()
        try:
            cw = self.wm.get(self.wm.current)
            return cw.to_dict()
        except SplightConfigError:
            return {}

    def get_field_value(
        self, field: str, field_data: Any
    ) -> tuple[Any, str, bool]:
        try:
            return self.wm.get(field), field, False
        except WorkspaceNotFoundError:
            return None, field, True


class WorkspaceSettings(Workspace, BaseSettings, Singleton):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            WorkspaceConfigSource(settings_cls=cls),
        )


class DatalakeClientType(str, Enum):
    LOCAL = "local"
    SYNC = "sync"
    BUFFERED_SYNC = "buffered_sync"
    BUFFERED_ASYNC = "buffered_async"


class DatalakeSettings(BaseSettings, Singleton):
    DL_CLIENT_TYPE: DatalakeClientType = DatalakeClientType.BUFFERED_ASYNC
    DL_BUFFER_SIZE: int = 500
    DL_BUFFER_TIMEOUT: float = 60  # seconds


class SplightAPIVersionSettings(BaseSettings, Singleton):
    API_VERSION: SplightAPIVersion = SplightAPIVersion.V3


# Create singletons
workspace_settings = WorkspaceSettings()
datalake_settings = DatalakeSettings()
api_settings = SplightAPIVersionSettings()
