import logging
from enum import Enum, IntEnum


class ChoiceMixin(str, Enum):
    @classmethod
    def choices(cls):
        return [(key.value.lower(), key.name.capitalize()) for key in cls]


class SeverityType(ChoiceMixin):
    system = 'system'
    info = 'info'
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'


class AlertStatus(ChoiceMixin):
    ALERT = "alert"
    NO_ALERT = "no_alert"
    NO_DATA = "no_data"


class AlertOperator(ChoiceMixin):
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "ge"
    LOWER_THAN = "lt"
    LOWER_THAN_OR_EQUAL = "le"
    EQUAL = "eq"


class AlertVariableType(ChoiceMixin):
    STR = "str"
    INT = "int"
    FLOAT = "float"


class ComponentSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"
    very_large = "very_large"

    def __str__(self):
        return self.value


class LogginLevel(IntEnum):
    critical = logging.CRITICAL
    error = logging.ERROR
    warning = logging.WARNING
    info = logging.INFO
    debug = logging.DEBUG
    notset = logging.NOTSET

    def __str__(self):
        return str(self.value)

    @classmethod
    def _missing_(cls, value):
        return super()._missing_(int(value))


class RestartPolicy(str, Enum):
    ALWAYS = "Always"
    ON_FAILURE = "OnFailure"
    NEVER = "Never"


class DeploymentStatus(str, Enum):
    STOPPED = "Stopped"
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class MinComponentCapacity(ChoiceMixin):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    VERY_LARGE = 'very_large'


class ComponentStatus(ChoiceMixin):
    STOPPED = "Stopped"
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class PrivacyPolicy(ChoiceMixin):
    PUBLIC = "public"
    PRIVATE = "private"


class VerificationLevel(ChoiceMixin):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    OFFICIAL = "official"


class BuildStatus(ChoiceMixin):
    PENDING = "pending"
    BUILDING = "building"
    FAILED = "failed"
    SUCCESS = "success"
    UNKNOWN = "unknown"


class ComponentType(ChoiceMixin):
    ALGORITHM = "algorithm"
    NETWORK = "network"
    CONNECTOR = "connector"
    SIMULATOR = "simulator"
