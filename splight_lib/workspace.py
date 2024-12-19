from functools import wraps
from pathlib import Path
from typing import Callable, Dict, List

import yaml
from pydantic import BaseModel

CONFIG_FILE = Path.home() / ".splight" / "config"


class Workspace(BaseModel):
    SPLIGHT_ACCESS_ID: str | None = None
    SPLIGHT_SECRET_KEY: str | None = None
    SPLIGHT_PLATFORM_API_HOST: str = "https://api.splight-ai.com"

    @property
    def configured(self) -> bool:
        return self.SPLIGHT_ACCESS_ID and self.SPLIGHT_SECRET_KEY


class SplightConfig(BaseModel):
    current_workspace: str = "default"
    workspaces: Dict[str, Workspace] = {"default": Workspace()}


class WorkspaceError(Exception):
    pass


class WorkspaceNotFoundError(WorkspaceError):
    def __init__(self, workspace: str):
        super().__init__(f"Workspace '{workspace}' does not exist")


class ActiveWorkspaceError(WorkspaceError):
    def __init__(self, workspace: str):
        super().__init__(f"Cannot delete active workspace '{workspace}'")


class WorkspaceExistsError(WorkspaceError):
    def __init__(self, workspace: str):
        super().__init__(f"Workspace '{workspace}' already exists")


class WorkspaceManager:
    def __init__(self, config_path: Path | str = CONFIG_FILE):
        self._config_path = Path(config_path)

        if not self._config_path.exists():
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            self._save(SplightConfig())

        self._config = SplightConfig.model_validate(
            yaml.safe_load(self._config_path.read_text()) or {}
        )

    def __repr__(self) -> str:
        lines = [f"WorkspaceManager(config_path='{self._config_path}')"]
        lines.append("Workspaces:")

        if not self._config.workspaces:
            lines.append("  No workspaces configured")
        else:
            for name, workspace in self._config.workspaces.items():
                current = (
                    " (current)"
                    if name == self._config.current_workspace
                    else ""
                )
                configured = (
                    " [configured]"
                    if workspace.configured
                    else " [not configured]"
                )
                lines.append(f"  - {name}{current}{configured}")
                lines.append(
                    f"      SPLIGHT_ACCESS_ID: {workspace.SPLIGHT_ACCESS_ID or 'None'}"
                )
                lines.append(
                    f"      SPLIGHT_SECRET_KEY: {workspace.SPLIGHT_SECRET_KEY or 'None'}"
                )
                lines.append(
                    f"      SPLIGHT_PLATFORM_API_HOST: {workspace.SPLIGHT_PLATFORM_API_HOST}"
                )

        return "\n".join(lines)

    def _save(self, config: SplightConfig):
        self._config_path.write_text(
            yaml.dump(config.model_dump(), default_flow_style=False)
        )

    @staticmethod
    def save(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._save(self._config)
            return result

        return wrapper

    def get(self, name: str) -> Workspace:
        if name not in self._config.workspaces:
            raise WorkspaceNotFoundError(name)

        return self._config.workspaces[name]

    @save
    def create(self, name: str, workspace: Workspace | None = None):
        if name in self._config.workspaces:
            raise WorkspaceExistsError(name)

        self._config.workspaces[name] = workspace or Workspace()

    @save
    def update(self, name: str, workspace: Workspace):
        if name not in self._config.workspaces:
            raise WorkspaceNotFoundError(name)

        self._config.workspaces[name] = workspace

    @save
    def delete(self, name: str):
        if name == self._config.current_workspace:
            raise ActiveWorkspaceError(name)

        if name not in self._config.workspaces:
            raise WorkspaceNotFoundError(name)

        del self._config.workspaces[name]

    @save
    def set_current(self, name: str):
        if name not in self._config.workspaces:
            raise WorkspaceNotFoundError(name)

        self._config.current_workspace = name

    @property
    def current(self) -> str:
        return self._config.current_workspace

    def list(self) -> List[str]:
        return list(self._config.workspaces.keys())
