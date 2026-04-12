import warnings
warnings.filterwarnings("ignore")

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict

# Try to import openenv base types; fall back to plain BaseModel if not installed.
try:
    from openenv.core.env_server.types import Action, Observation as _OpenenvObservation

    class SqlQueryAction(Action):
        """SQL query action — the agent submits a SQL SELECT statement."""
        model_config = ConfigDict(extra="allow", validate_assignment=True, arbitrary_types_allowed=True)
        sql_query: str = ""

    class SqlQueryObservation(_OpenenvObservation):
        """Observation returned by the SQL Query environment."""
        model_config = ConfigDict(extra="allow", validate_assignment=True, arbitrary_types_allowed=True)
        task_id: int = 0
        question: str = ""
        db_schema: str = ""       # renamed from 'schema' to avoid Pydantic BaseModel clash
        difficulty: str = "easy"
        feedback: str = ""
        executed_output: Optional[str] = None
        is_correct: bool = False

except ImportError:
    # Fallback when openenv-core is not installed (local dev / tests)
    class SqlQueryAction(BaseModel):  # type: ignore[no-redef]
        sql_query: str = ""

    class SqlQueryObservation(BaseModel):  # type: ignore[no-redef]
        task_id: int = 0
        question: str = ""
        db_schema: str = ""
        difficulty: str = "easy"
        reward: float = 0.0
        feedback: str = ""
        executed_output: Optional[str] = None
        is_correct: bool = False
        done: bool = False
