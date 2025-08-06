from pathlib import Path

import pytest

from splight_lib.client.database.abstract import AbstractDatabaseClient
from splight_lib.client.datalake.common.abstract import AbstractDatalakeClient
from splight_lib.settings import SplightAPIVersion, api_settings

# Only load these tests when API_VERSION is v4
API_V4_TESTS = Path("splight_lib/models/_v4")


@pytest.fixture(autouse=True)
def reset_singletons():
    AbstractDatabaseClient._instances = {}
    AbstractDatalakeClient._instances = {}


class VersionAwareDirectory(pytest.Directory):
    def collect(self):
        matching_files = [
            file
            for test_dir in self.path.rglob("*")
            if test_dir.is_dir() and test_dir.name in ("test", "tests")
            for file in test_dir.glob("test_*.py")
        ] + [
            file
            for test_dir in self.path.rglob("*")
            if test_dir.is_dir() and test_dir.name in ("test", "tests")
            for file in test_dir.glob("tests_*.py")
        ]
        for path in matching_files:
            if api_settings.API_VERSION == SplightAPIVersion.V4:
                if "_v3" in path.name:
                    continue
            elif api_settings.API_VERSION == SplightAPIVersion.V3:
                if "_v4" in path.name:
                    continue

            yield from self.ihook.pytest_collect_file(
                file_path=path, parent=self
            )


@pytest.hookimpl
def pytest_collect_directory(path, parent):
    return VersionAwareDirectory.from_parent(parent=parent, path=path)
