from typing import List, Union

from cryptography.fernet import Fernet
from pydantic import BaseSettings


class EncryptionSettings(BaseSettings):
    SPLIGHT_ENCRYPTION_KEY: str


def decrypt_value_validator(
    cls, value: Union[str, List[str]]
) -> Union[str, List[str]]:
    config = EncryptionSettings()
    encrypter = Fernet(config.SPLIGHT_ENCRYPTION_KEY.encode("utf-8"))
    if isinstance(value, list):
        decripted = [
            encrypter.decrypt(v.encode("utf-8")).decode("utf-8") for v in value
        ]
    else:
        decripted = encrypter.decrypt(value.encode("utf-8")).decode("utf-8")
    return decripted


def encrypt_value(value: Union[str, int, float]) -> str:
    string = f"{value}"
    config = EncryptionSettings()
    encrypter = Fernet(config.SPLIGHT_ENCRYPTION_KEY.encode("utf-8"))
    encrypted = encrypter.encrypt(string.encode("utf-8")).decode("utf-8")
    return encrypted
