class InvalidComponentObjectInstance(Exception):
    pass


class SecretNotFound(Exception):
    def __init__(self, name: str):
        msg = f"Secrent {name} not found in database"
        super().__init__(msg)


class SecretDecryptionError(Exception):
    def __init__(self, name: str):
        msg = f"Unable to decrypt secret {name}"
        super().__init__(msg)
