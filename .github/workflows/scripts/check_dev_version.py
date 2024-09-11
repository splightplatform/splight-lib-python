import sys

from pkg_resources import parse_version as parse


class VersionError(Exception):
    """Raised when the version is not a developer version."""

    ...


if __name__ == "__main__":
    """Checks if the version is a developer version.

    Parameters
    ----------
    version: The version from the feature branch

    Raises
    ------
    VersionError if the version is not a developer version
    """
    version_line = sys.argv[1]

    version = parse(version_line)

    if not (version.is_prerelease or version.is_devrelease):
        raise VersionError(f"Version {version} is not a developer version")
