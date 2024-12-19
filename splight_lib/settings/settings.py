from typing import Any

from pydantic import ConfigDict
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from .workspace import SplightConfigManager, Workspace, WorkspaceError


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
        except WorkspaceError:
            return {}

    def get_field_value(
        self, field: str, field_data: Any
    ) -> tuple[Any, str, bool]:
        value = None
        try:
            ...

        except Exception:
            pass
        return value, "workspace-config", False


class SplightSettings(Workspace, BaseSettings, Singleton):
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


class DatalakeSettings(BaseSettings, Singleton):
    DL_CLIENT_TYPE: DatalakeClientType = DatalakeClientType.BUFFERED_ASYNC
    DL_BUFFER_SIZE: int = DL_BUFFER_SIZE
    DL_BUFFER_TIMEOUT: float = DL_BUFFER_TIMEOUT  # seconds


# Create singletons
settings = SplightSettings()
datalake_settings = DatalakeSettings()
