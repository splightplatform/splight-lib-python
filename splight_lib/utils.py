from cryptography.fernet import Fernet
from splight_lib.settings import setup


ENCRYPTION_KEY = setup.settings.SPLIGHT_ENCRYPTION_KEY


def decrypt_value_validator(cls, value: str) -> str:
    encrypter = Fernet(ENCRYPTION_KEY.encode("utf-8"))
    decripted = encrypter.decrypt(value.encode("utf-8")).decode("utf-8")
    return decripted
