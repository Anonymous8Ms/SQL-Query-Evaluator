from pydantic import BaseModel, ConfigDict, Field

try:
    from openenv.core.types import Action, Observation
except ImportError:  # pragma: no cover - compatibility with older or missing OpenEnv installs
    try:
        from openenv.core.env_server.types import Action, Observation
    except ImportError:  # pragma: no cover - allow local testing without openenv-core
        class Action(BaseModel):
            pass

        class Observation(BaseModel):
            pass


class SqlQueryAction(Action):
    sql_query: str = Field(..., description="The SQL query to execute")


class SqlQueryObservation(Observation):
    db_schema: str = Field(..., description="The database schema information")
    question: str = Field(..., description="The SQL question to solve")
    difficulty: str = Field(..., description="Task difficulty level")
    reward: float = Field(0.0, description="Reward from the last action")
    done: bool = Field(False, description="Whether the episode is finished")
    feedback: str = Field("", description="Feedback on the last query")
