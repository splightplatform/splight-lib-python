
class InstanceNotFound(Exception):
    def __init__(self, name: str, uid: str):
        self._msg = f"Object {uid} of type {name} not found in database"

    def __str__(self) -> str:
        return self._msg
