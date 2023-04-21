from pydantic import BaseModel


class SplightBaseModel(BaseModel):
    def __hash__(self):  # make hashable BaseModel subclass
        return hash(self.__class__.__name__ + str(tuple(self.dict().values())))

    @staticmethod
    def get_event_name(type: str, action: str) -> str:
        return f"{type.lower()}-{action.lower()}"

    @classmethod
    def class_name(cls):
        """Get class name of the model from the repr string
        Class attribute is mapped to the metaclass.
        """
        clean_path = "".join([c for c in str(cls) if c.isalpha() or c =="."])
        class_name = clean_path.split(".")[-1]
        return class_name