class InvalidReference(Exception):
    pass


class CyclicReference(Exception):
    pass


class DuplicatedAttribute(Exception):
    pass


class CrossNamespaceTryException(Exception):
    def __init__(self, namespace, conflicts, *args, **kwargs) -> None:
        self.namespace = namespace
        self.conflicts = conflicts
        message = f"Found conflicts in fields: {conflicts}. Current tenant: {self.tenant}"
        super().__init__(message, *args, **kwargs)


class TriggerGroupLimitException(Exception):
    def __init__(self, *args, **kwargs) -> None:
        message: str = "You have exceeded the maximum number of triggers per group."
        super().__init__(message, *args, **kwargs)