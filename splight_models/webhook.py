from pydantic import BaseModel
from splight_models import SplightBaseModel
from splight_models.exception import InvalidModel
import splight_models as spmodels


class WebhookEvent(BaseModel):
    object_type: str
    data: SplightBaseModel

    @classmethod
    def from_event_dict(cls, event_dict):
        model_name = event_dict["object_type"]
        model_class = getattr(spmodels, model_name, None)
        if model_class is None:
            raise InvalidModel(model_name)

        instance = model_class.parse_obj(event_dict["data"])
        return cls(object_type=model_name, data=instance)
