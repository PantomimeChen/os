from dataclasses import dataclass
from enum import Enum

class ProcessState(str, Enum):
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    TERMINATED = "TERMINATED"

@dataclass
class ProcSpec:
    pid: int
    arrival: int
    burst: int
    priority: int = 0

@dataclass
class TimelineSlice:
    pid: int
    start: int
    end: int
    core: int = 0

