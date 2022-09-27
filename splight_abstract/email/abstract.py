from abc import abstractmethod
from pydantic import BaseSettings
from datetime import timedelta
from splight_abstract.client import AbstractClient
from typing import List, Union, Dict, Optional
from splight_models import EmailType

class EmailUnsubscribeGroups(BaseSettings):
    TC_UNSUBSCRIBE_GROUP_ID: int = 0

class EmailTemplates(BaseSettings):
    TC_TEMPLATE_ID: str = ""

class EmailLists(BaseSettings):
    NEWSLETTER_LIST_ID: str = ""
    ORGANIZATIONS_LIST_ID: str = ""

class AbstractEmailClient(AbstractClient):
    def __init__(self, *args, **kwargs):
        self.lists = EmailLists()
        self.templates = EmailTemplates()
        self.unsubscribe_groups = EmailUnsubscribeGroups()
        super().__init__(*args, **kwargs)

    @abstractmethod
    def send(self, subject: str, to: Union[str, List[str]], variables: Dict, template: Optional[str] = None, type: EmailType = EmailType.INFO):
        pass

    @abstractmethod
    def send_to_list(self, name: str, template_id: str, list_id: str, unsubscribe_group_id: int, delay: Optional[timedelta] = None) -> None:
        pass

    @abstractmethod
    def add_contact_to_list(self, list_id: str, data: Dict) -> None:
        pass