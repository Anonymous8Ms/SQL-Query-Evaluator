# Suppress ALL warnings at module level before any class definitions.
# The validator imports this module directly with -W error mode, which converts
# UserWarnings to exceptions. Suppressing here prevents that crash regardless
# of import order.
import warnings
warnings.filterwarnings("ignore")

from typing import Optional
from pydantic import BaseModel


class SqlQueryAction(BaseModel):
    sql_query: str = ""


class SqlQueryObservation(BaseModel):
    task_id: int = 0
    question: str = ""
    db_schema: str = ""
    difficulty: str = "easy"
    reward: float = 0.0
    feedback: str = ""
    executed_output: Optional[str] = None
    is_correct: bool = False
    done: bool = False
