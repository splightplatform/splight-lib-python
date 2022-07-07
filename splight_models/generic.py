class GenericModel:
    def __init__(self, *args, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
