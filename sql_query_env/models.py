from dataclasses import dataclass
from typing import Optional

@dataclass
class SqlQueryAction:
    sql_query: str

@dataclass
class SqlQueryObservation:
    question: str
    schema: str
    difficulty: str
    reward: float
    done: bool
    feedback: Optional[str] = None
