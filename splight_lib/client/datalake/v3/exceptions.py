class DatalakeRequestError(Exception):
    def __init__(self, status_code: int, message: str):
        self._msg = f"Request failed with status code {status_code}: {message}"
        super().__init__(self._msg)


class InvalidCollectionName(Exception):
    def __init__(self, collection: str):
        self._msg = f"Collection {collection} is not a valid collection"

    def __str__(self) -> str:
        return self._msg
