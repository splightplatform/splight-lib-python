class InvalidCronString(Exception):
    def __init__(self, cron_str: str):
        self._msg = (
            f"Invalid cron string: {cron_str}. "
            f"Expected format: 'minute hour day_of_month month day_of_week'"
        )

    def __str__(self):
        return self._msg
