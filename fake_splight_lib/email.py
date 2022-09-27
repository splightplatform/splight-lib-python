from splight_abstract import AbstractEmailClient
from typing import List, Union, Dict, Optional
from datetime import timedelta
from splight_models import EmailType
from splight_lib import logging

logger = logging.getLogger()

class FakeEmailClient(AbstractEmailClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send(self, subject: str, to: Union[str, List[str]], variables: Dict, template: Optional[str] = None, type: EmailType = EmailType.INFO):
        logger.info(f"[FAKED] Email sent to {to}")

    def send_to_list(self, name: str, template_id: str, list_id: str, unsubscribe_group_id: int, delay: Optional[timedelta] = None) -> None:
        logger.info(f"[FAKED] Sent template {template_id} to all organizations")

    def add_contact_to_list(self, list_id: str, data: Dict) -> None:
        logger.info(f"[FAKED] Added contact to list {list_id}")