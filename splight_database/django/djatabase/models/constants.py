SYSTEM = 'system'
INFO = 'info'
LOW = 'low'
MEDIUM = 'medium'
HIGH = 'high'
CRITICAL = 'critical'


SEVERITIES = (
    (SYSTEM, 'System'),
    (INFO, 'Info'),
    (LOW, 'Low'),
    (MEDIUM, 'Medium'),
    (HIGH, 'High'),
    (CRITICAL, 'Critical'),
)

GREATER_THAN = 'gt'
GREATER_THAN_OR_EQUAL = 'ge'
LOWER_THAN = 'lt'
LOWER_THAN_OR_EQUAL = 'le'
EQUAL = 'eq'


OPERATORS = (
    (GREATER_THAN, 'Greater than'),
    (GREATER_THAN_OR_EQUAL, 'Greater or equal'),
    (LOWER_THAN, 'Lower than'),
    (LOWER_THAN_OR_EQUAL, 'Lower than or equal'),
    (EQUAL, 'Equal'),
)

SOURCE_TYPE = (
    'Algorithm',
    'Network',
    'Connector',
)
