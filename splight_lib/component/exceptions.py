class DuplicatedComponentException(Exception):
    def __init__(self, component_id: str):
        msg = f"Component with the id {component_id} is running."
        super().__init__(msg)


class DuplicatedValuesError(Exception):
    pass


class ParameterDependencyError(Exception):
    pass


class MissingSetPointCallback(Exception):
    def __init__(self, method_name: str):
        msg = f"Missing method {method_name} associated with a SetPoint"
        super().__init__(msg)
