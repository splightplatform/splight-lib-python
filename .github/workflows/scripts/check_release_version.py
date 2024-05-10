import sys

from pkg_resources import parse_version as parse

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
    parse(string_version)
