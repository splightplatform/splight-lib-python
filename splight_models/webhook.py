from typing import Optional, Dict
from pydantic import Field
from datetime import datetime, timezone
from splight_models import SplightBaseModel, User
from splight_models.exception import InvalidModel
import splight_models as spmodels


class WebhookEvent(SplightBaseModel):
    event_name: str
    id: Optional[str] = None
    instance_id: Optional[str] = None
    socket_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))  # pusher cannot json serialize datetime objects
    display_text: Optional[str] = None
    user: Optional[User] = None
    data: Dict

    @classmethod
    def from_event_dict(cls, event_dict):
        model_name = event_dict["object_type"]
        model_class = getattr(spmodels, model_name, None)
        if model_class is None:
            raise InvalidModel(model_name)

        instance = model_class.parse_obj(event_dict["data"])
        return cls(object_type=model_name, data=instance)
