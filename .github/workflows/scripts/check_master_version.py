import sys

from pkg_resources import parse_version as parse


class VersionError(Exception):
    """Raised when the feature version is not greater than the master
    version."""


if __name__ == "__main__":
    """Compares versions between the local repository and master.

    Args:
        old_version (arg 1) (str): local version number (x.y.z)
        new_version (arg 2) (str): master version number (x.y.x)
    Raises:
        VersionError: if the local version is not greater than master version
    """
    old_version_line = sys.argv[1]
    new_version_line = sys.argv[2]

    master_version = parse(old_version_line)
    project_version = parse(new_version_line)

    if project_version <= master_version:
        raise VersionError(
            f"Feature version {project_version} is not greater than "
            f"master version {master_version}"
        )
