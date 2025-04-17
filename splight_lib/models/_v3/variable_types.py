from datetime import datetime

from pydantic import AnyUrl

from splight_lib.execution.scheduling import Crontab

NATIVE_TYPES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "datetime": datetime,
    "url": AnyUrl,
}

CUSTOM_TYPES = {
    "crontab": Crontab,
}
