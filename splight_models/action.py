from enum import Enum

class Action(str, Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    WRITE = "write"
    UPDATE = "update"
    OPERATE = "operate"