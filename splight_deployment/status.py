from pydantic import BaseModel


class Status(BaseModel):
    """
    Status model
    """
    id: int
    deployment_name: str
    status: str
    detail: str = ""
