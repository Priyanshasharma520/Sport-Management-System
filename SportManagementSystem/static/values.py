from enum import Enum

class EventType(Enum):
    PREPLAY = "PREPLAY"
    INPLAY = "INPLAY"
    

class EventStatus(Enum):
    
    PENDING = "PENDING"
    STARTED = "STARTED"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"
    
class SelectionOutcome(Enum):
    UNSETTLED = "UNSETTLED"
    VOID = "VOID"
    LOSE = "LOSE"
    WIN = "WIN"