from pathlib import Path

import pytest

from splight_lib.client.database.abstract import AbstractDatabaseClient
from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.settings import SplightAPIVersion, api_settings

# Only load these tests when API_VERSION is v4
API_V4_TESTS = Path("splight_lib/models/_v4")


@pytest.fixture(autouse=True)
def reset_singletons():
    AbstractDatabaseClient._instances = {}
    AbstractDatalakeClient._instances = {}


class VersionAwareDirectory(pytest.Directory):
    def collect(self):
        # If API_VERSION is v4, only collect tests from the _v4 directory
        if api_settings.API_VERSION == SplightAPIVersion.V4:
            # Only collect tests inside splight_lib/models/_v4
            if self.path.is_relative_to(Path.cwd() / API_V4_TESTS):
                for path in self.path.glob("test_*.py"):
                    yield from self.ihook.pytest_collect_file(
                        file_path=path, parent=self
                    )
            return  # Skip other directories

        # If API_VERSION is v3, collect tests from all directories (excluding _v4)
        elif api_settings.API_VERSION == SplightAPIVersion.V3:
            if not self.path.is_relative_to(Path.cwd() / API_V4_TESTS):
                # Collect tests from all directories except _v4
                for path in self.path.glob("test_*.py"):
                    yield from self.ihook.pytest_collect_file(
                        file_path=path, parent=self
                    )
            return  # Skip collection if it is the v4 directory in v3 mode


@pytest.hookimpl
def pytest_collect_directory(path, parent):
    return VersionAwareDirectory.from_parent(parent=parent, path=path)
