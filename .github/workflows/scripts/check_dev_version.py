import sys

import pkg_resources


class InvalidDeveloperVersion(Exception):
    """Raised when the version is not a valid developer version."""


if __name__ == "__main__":
    """Verify if the format is developer for a given string version.

    Example:
        - x.y.z-dev0: it's OK.
        - x.y.x: raises VersionError

    Args:
        version (arg 1) (str): current lib version number (x.y.z-dev0)
    Raises:
        VersionError: if the current version is not a developer version.
    """
    string_version = sys.argv[1]
    version = pkg_resources.parse_version(string_version)

    if not version.is_prerelease:
        raise InvalidDeveloperVersion(
            f"Current library version {string_version} is not a valid "
            "developer version"
        )
