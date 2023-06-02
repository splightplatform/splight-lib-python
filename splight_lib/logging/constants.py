from typing import Literal, get_args

LogType = Literal["dev", "components"]

LOGGING_DEV, LOGGING_COMPONENTS = get_args(LogType)
