"""
SQL Query Evaluator - Core Models
Pydantic models for environment state, actions, and observations
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TaskCategory(str, Enum):
    AGGREGATION = "aggregation"
    JOINS = "joins"
    FILTERING = "filtering"
    SUBQUERIES = "subqueries"


class Observation(BaseModel):
    """Environment observation returned after reset or step"""
    task_id: int
    task_description: str
    db_schema: str
    current_query: str = ""
    expected_columns: List[str]
    sample_output: Optional[str] = None
    max_steps: int = 10
    current_step: int = 0
    difficulty: str


class Action(BaseModel):
    """Agent action: SQL query to submit"""
    sql_query: str
    submit: bool = False


class StepResult(BaseModel):
    """Result of a step operation"""
    observation: Observation
    reward: float = Field(..., ge=0.0, le=1.0)
    done: bool = False
    info: Dict[str, Any] = Field(default_factory=dict)


class EnvironmentState(BaseModel):
    """Current state of the environment"""
    task_id: int
    current_step: int
    max_steps: int
    is_done: bool
    last_reward: float
    total_reward: float
    sql_history: List[str] = Field(default_factory=list)
    difficulty: str


class Task(BaseModel):
    """Task definition"""
    task_id: int
    name: str
    description: str
    difficulty: DifficultyLevel
    category: TaskCategory
    db_schema: str
    expected_query: str
    test_cases: List[Dict[str, Any]]
    hints: List[str] = Field(default_factory=list)
    max_steps: int = 10


class GradeResult(BaseModel):
    """Grading result for SQL query evaluation"""
    score: float = Field(..., ge=0.0, le=1.0)
    is_correct: bool
    message: str
    matched_rows: int
    expected_rows: int
    missing_columns: List[str] = Field(default_factory=list)
    extra_columns: List[str] = Field(default_factory=list)


class ResetRequest(BaseModel):
    """Request body for reset endpoint"""
    task_id: Optional[int] = None


class StepRequest(BaseModel):
    """Request body for step endpoint"""
    sql_query: str
    submit: bool = False


# ── Internal Compatibility Models ─────────────────────────────────────────────

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
