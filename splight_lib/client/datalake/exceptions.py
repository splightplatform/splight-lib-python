class InvalidCollectionName(Exception):
    def __init__(self, collection: str):
        self._msg = f"Collection {collection} is not a valid collection"

    def __str__(self) -> str:
        return self._msg
