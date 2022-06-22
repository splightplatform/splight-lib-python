from enum import Enum
from splight_database.django.djatabase.models.constants import (INFO, SYSTEM, LOW, MEDIUM, HIGH, CRITICAL)


class SeverityType(str, Enum):
    system = SYSTEM
    info = INFO
    low = LOW
    medium = MEDIUM
    high = HIGH
    critical = CRITICAL
