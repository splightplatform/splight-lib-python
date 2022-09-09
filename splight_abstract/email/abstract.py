from abc import abstractmethod
from splight_abstract.client import AbstractClient
from typing import List, Union
from splight_models import EmailType

class AbstractEmailClient(AbstractClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def send(self, subject: str, message: str, to: Union[str, List[str]], type: EmailType = EmailType.INFO):
        pass

    @abstractmethod
    def add_to_newsletter(self, email: str) -> None:
        pass