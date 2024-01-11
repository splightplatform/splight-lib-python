from datetime import datetime, timezone
from typing import Dict, List


class DatalakeDocumentBuffer:
    """A simple buffer implementation for datalake documents."""

    def __init__(self, buffer_size: int, buffer_timeout: float):
        self._size = buffer_size
        self._timeout = buffer_timeout
        self._buffer: List[Dict] = []
        self._last_flush = datetime.now(timezone.utc)

        self.reset()

    @property
    def data(self) -> List[Dict]:
        """Retrieves the buffer data

        Returns
        -------
        List[Dict] a list with the documents
        """
        return self._buffer

    def should_flush(self) -> bool:
        """Method used to check if the buffer should be flushed

        Returns
        -------
        bool: True if the buffer should be flushed, False otherwise
        """
        exist_data = True if self._buffer else False
        now = datetime.now(timezone.utc)
        delta = (now - self._last_flush).total_seconds()
        timeout_cond = delta >= self._timeout

        size_cond = len(self._buffer) >= self._size
        return (timeout_cond or size_cond) and exist_data

    def reset(self) -> None:
        """Resets the buffer to the empty state with not stored data and the
        flushed date to the called time.
        """
        self._last_flush = datetime.now(timezone.utc)
        self._buffer = []

    def add_documents(self, documents: List[Dict]):
        """Adds new documents to the buffer.

        Parameters
        ----------
        documents: List[Dict] a list of new documents to add to the buffer.
        """
        self._buffer.extend(documents)
