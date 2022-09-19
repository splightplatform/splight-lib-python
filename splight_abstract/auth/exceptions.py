class AuthenticationError(Exception):
    def __init__(self, url: str):
        self._msg = "An error ocurred during authentication"

    def __str__(self) -> str:
        return self._msg
