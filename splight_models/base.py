from pydantic import BaseModel


class SplightBaseModel(BaseModel):
    def __hash__(self):  # make hashable BaseModel subclass
        return hash(self.__class__.__name__ + str(tuple(self.dict().values())))

    @staticmethod
    def get_event_name(type: str, action: str) -> str:
        return f"{type.lower()}-{action.lower()}"
