from typing import Optional

from pydantic import BaseSettings
from splight_lib.encryption import EncryptionClient

from .base import SplightBaseModel


class Secret(SplightBaseModel):
    id: Optional[str] = None
    name: str
    value: str

    def decrypt(self):
        encryption_client = EncryptionClient()
        return encryption_client.decrypt(self.value)
