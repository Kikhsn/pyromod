from enum import Enum, auto


class ListenerTypes(Enum):
    MESSAGE = auto()
    CALLBACK_QUERY = auto()
    MIXED = auto()
