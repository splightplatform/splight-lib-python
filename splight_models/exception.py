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


class LockedGraphException(Exception):
    pass


class CrossGraphException(Exception):
    pass


class InvalidModel(Exception):
    def __init__(self, model_name: str):
        self._msg = f"Model {model_name} is not a valid Splight model"

    def __str__(self) -> str:
        return self._msg
