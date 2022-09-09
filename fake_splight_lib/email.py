from splight_abstract import AbstractEmailClient
from typing import List, Union
from splight_models import EmailType
from splight_lib import logging

logger = logging.getLogger()

class FakeEmailClient(AbstractEmailClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send(self, subject: str, message: str, to: Union[str, List[str]], type: EmailType = EmailType.INFO):
        logger.info(f"[FAKED] Email sent to {to}")

    def add_to_newsletter(self, email: str) -> None:
        logger.info(f"[FAKED] Added {email} to newsletter")