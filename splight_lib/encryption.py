from functools import cached_property
from cryptography.fernet import Fernet as Branca
from typing import Optional
from pydantic import BaseSettings


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
            return value
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str):
        if not self.key:
            return value
        return self.fernet.decrypt(value.encode()).decode()

    def encrypt_file(self, path: str):
        if not self.key:
            return None
        with open(path, 'rb+') as f:
            original = f.read()
        with open(path, 'wb') as f:
            f.seek(0)
            encrypted = self.fernet.encrypt(original)
            f.write(encrypted)

    def decrypt_file(self, path: str):
        if not self.key:
            return
        with open(path, 'rb+') as f:
            original = f.read()
        with open(path, 'wb') as f:
            f.seek(0)
            decrypted = self.fernet.decrypt(original)
            f.write(decrypted)
