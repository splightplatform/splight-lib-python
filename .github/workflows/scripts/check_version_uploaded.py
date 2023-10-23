import json
import sys
import urllib.request

from pkg_resources import parse_version as parse


class PypiVersionError(Exception):
    """Raised if the local version was already uploaded to pypi."""


def get_pypi_versions(project_name: str):
    url = f"https://pypi.org/pypi/{project_name}/json"
    response = urllib.request.urlopen(url)
    return [parse(r) for r in json.loads(response.read())["releases"].keys()]


if __name__ == "__main__":
    """Checks the version was not uploaded.

    Args:
        local_version (arg 1) (str): local version number (x.y.z)
        project_name (arg 2) (str): name of the project on pypi
    Raises:
        PypiVersionError: if the local version was already uploaded to pypi
    """
    local_version = sys.argv[1]
    project_name = sys.argv[2]

    project_version = parse(local_version)
    uploaded_versions = get_pypi_versions(project_name)
    if project_version in uploaded_versions:
        raise PypiVersionError(
            f"Feature version {project_version} is already uploaded to pypi."
        )
