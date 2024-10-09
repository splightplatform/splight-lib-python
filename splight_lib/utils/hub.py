import json
import os
from typing import Any

import pathspec

SPLIGHT_IGNORE = ".splightignore"
COMPRESSION_TYPE = "7z"
SPEC_FILE = "spec.json"
RUN_FILE = "run.sh"
README_FILE_1 = "README.md"
README_FILE_2 = "README"


def get_spec(path: str) -> dict[str, Any]:
    with open(os.path.join(path, SPEC_FILE)) as fid:
        return json.load(fid)


def get_ignore_pathspec(path: str) -> pathspec.PathSpec | None:
    try:
        with open(os.path.join(path, SPLIGHT_IGNORE), "r") as splightignore:
            return pathspec.PathSpec.from_lines("gitwildmatch", splightignore)
    except FileNotFoundError:
        return None
