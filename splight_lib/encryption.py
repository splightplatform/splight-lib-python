from functools import cached_property
from cryptography.fernet import Fernet as Branca
from pydantic import BaseSettings


class EncryptionSettings(BaseSettings):
    SPLIGHT_ENCRYPTION_KEY: str = ""


encryption_settings = EncryptionSettings()


class EncryptionKey:
    key = encryption_settings.SPLIGHT_ENCRYPTION_KEY


class EncryptionManager:
    def __init__(self):
        self._fernet = None
        self.key = EncryptionKey.key

    @cached_property
    def fernet(self):
        if not self._fernet:
            self._fernet = Branca(self.key)
        return self._fernet

    def encrypt(self, value: str):
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str):
        return self.fernet.decrypt(value.encode()).decode()

    def encrypt_file(self, path: str):
        with open(path, 'rb+') as f:
            original = f.read()
        with open(path, 'wb') as f:
            f.seek(0)
            encrypted = self.fernet.encrypt(original)
            f.write(encrypted)

    def decrypt_file(self, path: str):
        with open(path, 'rb+') as f:
            original = f.read()
        with open(path, 'wb') as f:
            f.seek(0)
            decrypted = self.fernet.decrypt(original)
            f.write(decrypted)
