import os
from typing import Optional
import pathspec

SPLIGHT_IGNORE = ".splightignore"  # TODO: move this to settings
COMPRESSION_TYPE = "7z"


def get_ignore_pathspec(path: str) -> Optional[pathspec.PathSpec]:
    try:
        with open(
            os.path.join(path, SPLIGHT_IGNORE), "r"
        ) as splightignore:
            return pathspec.PathSpec.from_lines(
                "gitwildmatch", splightignore
            )
    except FileNotFoundError:
        return None
