from typing import Optional
from pydantic import BaseModel


class SqlQueryAction(BaseModel):
    sql_query: str


class SqlQueryObservation(BaseModel):
    task_id: int
    question: str
    db_schema: str = ""
    difficulty: str
    reward: float
    feedback: str
    executed_output: Optional[str] = None
    is_correct: bool
    done: bool
