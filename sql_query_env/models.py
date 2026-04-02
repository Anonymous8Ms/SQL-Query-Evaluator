from dataclasses import dataclass

@dataclass
class SQLAction:
    query: str


@dataclass
class SQLObservation:
    score: float
    feedback: str
    done: bool
