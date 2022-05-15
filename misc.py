from enum import Enum

HEIGHT = 256

class Status(Enum):
    """Possible status of every tile."""

    VISITED = 0
    UNVISITED = 1
    NONTRAVERSABLE = 2
