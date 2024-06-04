class MethodNotAllowed(Exception):
    pass


class InvalidObjectInstance(Exception):
    pass


class SecretNotFound(Exception):
    def __init__(self, name: str):
        msg = f"Secret {name} not found in database"
        super().__init__(msg)


class SecretDecryptionError(Exception):
    def __init__(self, name: str):
        msg = f"Unable to decrypt secret {name}"
        super().__init__(msg)


class InvalidFunctionConfiguration(Exception):
    pass


class MissingFunctionItemExpression(Exception):
    pass


class InvalidAlertConfiguration(Exception):
    pass


class MissingAlertItemExpression(Exception):
    pass


class ForbiddenOperation(Exception):
    pass


class InvalidConfigType(Exception):
    def __init__(self, name: str, type_: str):
        msg = (
            f"Config parameter {name} has an invalid type {type_}. The only "
            "valid type is 'Asset'"
        )
        super().__init__(msg)


class InvalidResourceType(Exception):
    def __init__(self, name: str, type_: str):
        msg = (
            f"Resource {name} has an invalid type {type_}. The only "
            "valid type is 'Asset'"
        )
        super().__init__(msg)


class MissingAsset(Exception):
    def __init__(self, name: str):
        msg = f"Resource {name} is missing the asset value"
        super().__init__(msg)


class InvalidArgument(Exception):
    pass
