from enum import Enum


class SeverityType(str, Enum):
    system = 'system'
    info = 'info'
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'
