from typing import Optional, Dict
from pydantic import Field
from datetime import datetime, timezone
from splight_models import SplightBaseModel, User
from splight_models.exception import InvalidModel
import splight_models as spmodels


class WebhookEvent(SplightBaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))  # pusher cannot json serialize datetime objects
    event_name: str
    object_type: Optional[str] = None
    object_id: Optional[str] = None
    data: Dict

    @classmethod
    def from_event_dict(cls, event_dict):
        model_name = event_dict.get("object_type")
        model_class = getattr(spmodels, model_name, None)
        if model_class is None:
            raise InvalidModel(model_name)
        instance = model_class.parse_obj(event_dict["data"])
        return cls(object_type=model_name, data=instance)
