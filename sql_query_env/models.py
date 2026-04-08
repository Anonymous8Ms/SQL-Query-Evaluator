from openenv.core.env_server.types import Action, Observation
from pydantic import Field

class SqlQueryAction(Action):
    sql_query: str = Field(..., description="The SQL query to execute")

class SqlQueryObservation(Observation):
    question: str = Field(..., description="The SQL question to solve")
    schema: str = Field(..., description="The database schema information")
    difficulty: str = Field(..., description="Task difficulty level")
    reward: float = Field(0.0, description="Reward from the last action")
    done: bool = Field(False, description="Whether the episode is finished")
    feedback: str = Field("", description="Feedback on the last query")
