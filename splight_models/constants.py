# TODO remove this file
import logging
from enum import Enum, IntEnum

class ChoiceMixin():
    @classmethod
    def choices(cls):
        return [(key.value, key.name.capitalize()) for key in cls]


class SeverityType(str, Enum):
    system = 'system'
    info = 'info'
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'


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


class MinComponentCapacity(str, ChoiceMixin, Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    VERY_LARGE = 'very_large'


class ComponentStatus(str, ChoiceMixin, Enum):
    STOPPED = "Stopped"
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class PrivacyPolicy(str, ChoiceMixin, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class VerificationLevel(str, ChoiceMixin, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    OFFICIAL = "official"


class BuildStatus(str, ChoiceMixin, Enum):
    PENDING = "pending"
    BUILDING = "building"
    FAILED = "failed"
    SUCCESS = "success"
    UNKNOWN = "unknown"


class ComponentType(str, ChoiceMixin, Enum):
    ALGORITHM = "algorithm"
    NETWORK = "network"
    CONNECTOR = "connector"
    SIMULATOR = "simulator"



