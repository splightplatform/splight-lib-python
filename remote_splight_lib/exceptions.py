class InvalidModel(Exception):
    def __init__(self, model_name: str):
        self._msg = f"Model {model_name} is not a valid database model"

    def __str__(self) -> str:
        return self._msg
