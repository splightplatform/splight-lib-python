from .base import SplightBaseModel
from typing import Optional
from pydantic import BaseSettings
from splight_lib.encryption import EncryptionManager


class Secret(SplightBaseModel):
    id: Optional[str] = None
    name: str
    value: str

    def decrypt(self):
        encryption_manager = EncryptionManager()
        return encryption_manager.decrypt(self.value)
