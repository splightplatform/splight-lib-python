class AuthenticationError(Exception):
    def __init__(self, url: str, status_code: int):
        self._msg = (
            f"An error ocurred during authentication to {url} with status "
            f"code {status_code}"
        )

    def __str__(self) -> str:
        return self._msg
