from typing import Optional

from splight_lib.encryption import EncryptionClient
from splight_lib.models.base import SplightDatabaseBaseModel


class Secret(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    value: str

    def decrypt(self):
        encryption_client = EncryptionClient()
        return encryption_client.decrypt(self.value)
