from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class SQLAction(Action):
    sql_query: str = Field(..., description="SQL query string")


class SQLObservation(Observation):
    question: str
    schema: str
    difficulty: str
    reward: float
    done: bool
    feedback: str
