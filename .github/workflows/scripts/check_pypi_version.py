import json
import sys
from packaging.version import parse
import requests


class VersionError(Exception):
    """Raised when the version is not greater than the one on pypi"""
    pass


def get_pypi_version(project_name: str):
    url = f"https://pypi.org/pypi/{project_name}/json"
    response = requests.get(url)
    response.raise_for_status()
    version = json.loads(response.content)["info"]["version"]
    return parse(version)

if __name__ == "__main__":
    """Compares versions between the local repository
    and the package on pypi.

    Args:
        local_version (arg 1) (str): local version number (x.y.z)
        project_name (arg 2) (str): name of the project on pypi
    Raises:
        VersionError: if the local version is not greater than
            the one on pypi
    """
    local_version = sys.argv[1]
    project_name = sys.argv[2]

    project_version = parse(local_version)
    public_project_version = get_pypi_version(project_name)

    if project_version <= public_project_version:
        raise VersionError(
            f"Feature version {project_version} is not greater than "
            f"uploaded version {public_project_version}"
        )
