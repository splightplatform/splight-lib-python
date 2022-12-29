import logging
from enum import Enum, IntEnum


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


class ComponentType(str, Enum):
    # TODO: Remove this
    COMPONENT = "Component"
    ALGORITHM = "Algorithm"
    NETWORK = "Network"
    CONNECTOR = "Connector"
    SYSTEM = "System"


class DeploymentStatus(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class ComponentStatus(str, Enum):
    STOPPED = "Stopped"
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class PrivacyPolicy(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class VerificationLevel(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    OFFICIAL = "official"


class BuildStatus(str, Enum):
    PENDING = "pending"
    BUILDING = "building"
    FAILED = "failed"
    SUCCESS = "success"
    UNKNOWN = "unknown"
