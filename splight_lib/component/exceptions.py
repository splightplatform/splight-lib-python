class DuplicatedComponentException(Exception):
    def __init__(self, component_id: str):
        msg = f"Component with the id {component_id} is running."
        super().__init__(msg)


class DuplicatedValuesError(Exception):
    pass


class ParameterDependencyError(Exception):
    pass


class MissingBindingCallback(Exception):
    def __init__(self, binding_name: str):
        msg = f"Missing method {binding_name} associated with a Binding"
        super().__init__(msg)


class InvalidBidingObject(Exception):
    def __init__(self, model_name: str):
        msg = f"Model {model_name} is not a valid model for a binding"
        super().__init__(msg)


class MissingSetPointCallback(Exception):
    def __init__(self, method_name: str):
        msg = f"Missing method {method_name} associated with a SetPoint"
        super().__init__(msg)


class MissingCommandCallback(Exception):
    def __init__(self, method_name: str):
        msg = f"Missing method {method_name} associated with a Command"
        super().__init__(msg)
