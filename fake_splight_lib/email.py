from splight_abstract import AbstractEmailClient
from typing import List, Union, Dict, Optional
from splight_models import EmailType
from splight_lib import logging

logger = logging.getLogger()

class FakeEmailClient(AbstractEmailClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send(self, subject: str, to: Union[str, List[str]], variables: Dict, template: Optional[str] = None, type: EmailType = EmailType.INFO):
        logger.info(f"[FAKED] Email sent to {to}")

    def send_template_to_all_organizations(self, name: str, template_id: str, unsubscribe_group_id: int) -> None:
        logger.info(f"[FAKED] Sent template {template_id} to all organizations")

    def add_to_newsletter(self, email: str) -> None:
        logger.info(f"[FAKED] Added {email} to newsletter")

    def add_organization_contact(self, org_data: Dict) -> None:
        logger.info(f"[FAKED] Added {org_data} to organization contacts")