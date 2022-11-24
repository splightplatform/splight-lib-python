from typing import Union

from pydantic import BaseSettings
from cryptography.fernet import Fernet


class EncryptionSettings(BaseSettings):
    SPLIGHT_ENCRYPTION_KEY: str


def decrypt_value_validator(cls, value: str) -> str:
    config = EncryptionSettings()
    encrypter = Fernet(config.SPLIGHT_ENCRYPTION_KEY.encode("utf-8"))
    decripted = encrypter.decrypt(value.encode("utf-8")).decode("utf-8")
    return decripted


def encrypt_value(value: Union[str, int, float]) -> str:
    string = f"{value}"
    config = EncryptionSettings()
    encrypter = Fernet(config.SPLIGHT_ENCRYPTION_KEY.encode("utf-8"))
    encrypted = encrypter.encrypt(string.encode("utf-8")).decode("utf-8")
    return encrypted
