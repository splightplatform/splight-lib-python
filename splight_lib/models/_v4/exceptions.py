class InvalidOperation(Exception):
    def __init__(self, method: str):
        super().__init__(f"Invalid operation: {method} is not supported.")
