
class NotAllowedAction(Exception):
    def __init__(self, action: str):
        self._msg = f"Action {action} is not allowed"

    def __str__(self) -> str:
        return self._msg

class InvalidModel(Exception):
    def __init__(self, model_name: str):
        self._msg = f"Model {model_name} is not a valid database model"

    def __str__(self) -> str:
        return self._msg
