from typing import Dict, Any, Tuple
from openenv.core.env_server import Env
from ..models import SqlQueryAction, SqlQueryObservation
from .grader import grade_query
from .database import get_db_connection
from ..tasks import SQL_TASKS

class SqlQueryEnvironment(Env):
    def __init__(self):
        super().__init__()
        self._db = get_db_connection()
        self._task_idx = 0
        self._current_task = None

    def reset(self, config: Dict[str, Any] = None) -> Tuple[SqlQueryObservation, Dict[str, Any]]:
        self._task_idx = 0
        self._current_task = SQL_TASKS[self._task_idx]
        
        observation = SqlQueryObservation(
            question=self._current_task["question"],
            schema=self._current_task["schema"],
            difficulty=self._current_task["difficulty"],
            reward=0.0,
            done=False,
            feedback="Environment reset. solve the first task."
        )
        return observation, {"episode_id": "ep_0", "step_count": 0}

    def step(self, action: SqlQueryAction) -> Tuple[SqlQueryObservation, float, bool, Dict[str, Any]]:
        # Grade the query using Person 2 logic
        result = grade_query(
            ai_query=action.sql_query,
            task=self._current_task,
            db_connection=self._db
        )
        
        reward = result["score"]
        feedback = result["feedback"]
        
        # Advance to next task
        self._task_idx += 1
        done = self._task_idx >= len(SQL_TASKS)
        
        if not done:
            self._current_task = SQL_TASKS[self._task_idx]
            observation = SqlQueryObservation(
                question=self._current_task["question"],
                schema=self._current_task["schema"],
                difficulty=self._current_task["difficulty"],
                reward=reward,
                done=done,
                feedback=feedback
            )
        else:
            observation = SqlQueryObservation(
                question="No more tasks.",
                schema="",
                difficulty="",
                reward=reward,
                done=done,
                feedback=feedback
            )
            
        return observation, reward, done, {"step_count": self._task_idx}
