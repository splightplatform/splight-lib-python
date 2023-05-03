import json
import sys

import urllib3
from pkg_resources import parse_version as parse


class PypiVersionError(Exception):
    """Raised when the version is not greater than the one on pypi"""

    pass


def get_pypi_version(project_name: str):
    url = f"https://pypi.org/pypi/{project_name}/json"
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    version = json.loads(response.data)["info"]["version"]
    return version


if __name__ == "__main__":
    """Compares versions between the local repository
    and the package on pypi.

    Args:
        local_version (arg 1) (str): local version number (x.y.z)
        project_name (arg 2) (str): name of the project on pypi
    Raises:
        VersionError: if the local version is not greater than the one on pypi
    """
    local_version = sys.argv[1]
    project_name = sys.argv[2]

    project_version = parse(local_version)
    public_project_version = get_pypi_version(project_name)

    if project_version <= public_project_version:
        raise PypiVersionError(
            f"Feature version {project_version} is not greater than "
            f"uploaded version {public_project_version}"
        )
