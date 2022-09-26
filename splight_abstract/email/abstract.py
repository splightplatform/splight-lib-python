from abc import abstractmethod
from splight_abstract.client import AbstractClient
from typing import List, Union, Dict, Optional
from splight_models import EmailType

class AbstractEmailClient(AbstractClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def send(self, subject: str, to: Union[str, List[str]], variables: Dict, template: Optional[str] = None, type: EmailType = EmailType.INFO):
        pass

    @abstractmethod
    def send_template_to_all_organizations(self, name: str, template_id: str, unsubscribe_group_id: int) -> None:
        pass

    @abstractmethod
    def add_to_newsletter(self, email: str) -> None:
        pass

    @abstractmethod
    def add_organization_contact(self, org_data: Dict) -> None:
        pass
