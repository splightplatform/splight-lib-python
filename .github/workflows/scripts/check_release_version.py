import sys


class InvalidReleaseVersion(Exception):
    """Raised when the version is not a valid release version."""


def is_release_version(str_version: str) -> bool:
    try:
        _ = tuple(int(i) for i in str_version.split("."))
    except ValueError:
        return False
    else:
        return True


if __name__ == "__main__":
    """Verify if the format is release for a given string version.

    Example:
        - x.y.z: it's OK.
        - x.y.x.dev0: raises InvalidReleaseVersion

    Args:
        version (arg 1) (str): current lib version number (x.y.z)
    Raises:
        InvalidReleaseVersion: if the current version is not a release
        version.
    """
    string_version = sys.argv[1]
    if not is_release_version(string_version):
        raise InvalidReleaseVersion(
            f"Current library version {string_version} is not a valid "
            "release version."
        )
