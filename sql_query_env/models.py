from openenv.core.env_server.types import Action, Observation
from pydantic import Field
from typing import Optional

class SqlQueryAction(Action):
    sql_query: str = Field(..., description="SQL query string")

class SqlQueryObservation(Observation):
    question: str
    schema: str
    difficulty: str
    reward: float
    done: bool
    feedback: Optional[str] = None
