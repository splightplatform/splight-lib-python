from functools import cached_property
from typing import Optional

from cryptography.fernet import Fernet as Branca
from pydantic import BaseSettings
from splight_lib.logging._internal import LogTags, get_splight_logger

logger = get_splight_logger()


class EncryptionSettings(BaseSettings):
    SPLIGHT_ENCRYPTION_KEY: Optional[str] = None


class EncryptionClient:
    def __init__(self):
        self._fernet = None
        self._settings = EncryptionSettings()
        self.key = self.settings.SPLIGHT_ENCRYPTION_KEY

    @cached_property
    def settings(self):
        return self._settings

    @cached_property
    def fernet(self):
        if not self._fernet:
            self._fernet = Branca(self.key)
        return self._fernet

    def encrypt(self, value: str):
        if not self.key:
            logger.warning(
                "Returning non-encrypted value since encryption key was not found in the environment",
                tags=LogTags.SECRET,
            )
            return value
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str):
        if not self.key:
            logger.warning(
                "Returning encrypted value since encryption key was not found in the environment",
                tags=LogTags.SECRET,
            )
            return value
        return self.fernet.decrypt(value.encode()).decode()

    def encrypt_file(self, path: str):
        if not self.key:
            return None
        with open(path, "rb+") as f:
            original = f.read()
        with open(path, "wb") as f:
            f.seek(0)
            encrypted = self.fernet.encrypt(original)
            f.write(encrypted)

    def decrypt_file(self, path: str):
        if not self.key:
            return
        with open(path, "rb+") as f:
            original = f.read()
        with open(path, "wb") as f:
            f.seek(0)
            decrypted = self.fernet.decrypt(original)
            f.write(decrypted)
