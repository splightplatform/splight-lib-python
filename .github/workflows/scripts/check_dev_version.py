import sys


class InvalidDeveloperVersion(Exception):
    """Raised when the version is not a valid developer version."""


def is_developer_version(str_version: str) -> bool:
    return "dev" in str_version


if __name__ == "__main__":
    """Verify if the format is developer for a given string version.

    Example:
        - x.y.z-dev0: it's OK.
        - x.y.x: raises InvalidDeveloperVersion

    Args:
        version (arg 1) (str): current lib version number (x.y.z-dev0)
    Raises:
        InvalidDeveloperVersion: if the current version is not a developer
        version.
    """
    string_version = sys.argv[1]

    if not is_developer_version(string_version):
        raise InvalidDeveloperVersion(
            f"Current library version {string_version} is not a valid "
            "developer version."
        )
