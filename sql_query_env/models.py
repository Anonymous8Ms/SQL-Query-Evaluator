from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SqlQueryAction(BaseModel):
    """Action containing the SQL query to execute."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    sql_query: str = Field(..., description="The SQL query to execute")


class SqlQueryObservation(BaseModel):
    """Observation returned by the SQL Query environment."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    # Use db_schema — never "schema" (would shadow BaseModel.schema classmethod)
    db_schema: str = Field(default="", description="The database schema information")
    question: str = Field(default="", description="The SQL question to solve")
    difficulty: str = Field(default="", description="Task difficulty level")
    reward: float = Field(default=0.0, description="Reward from the last action")
    done: bool = Field(default=False, description="Whether the episode is finished")
    feedback: str = Field(default="", description="Feedback on the last query")
    executed_output: Optional[str] = Field(default=None, description="Query execution output")
    is_correct: bool = Field(default=False, description="Whether the query is correct")
    task_id: int = Field(default=0, description="Current task ID")
