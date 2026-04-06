from typing import Dict, Any, Tuple
from openenv.core.env_server import Env
from ..models import SqlQueryAction, SqlQueryObservation
from .grader import grade_query
from .database import get_db_connection
from ..tasks import SQL_TASKS

class SqlQueryEnvironment(Env):
    def __init__(self):
        super().__init__()
        self.db = get_db_connection()
        self.current_task_idx = 0

    def reset(self, config: Dict[str, Any] = None) -> Tuple[SqlQueryObservation, Dict[str, Any]]:
        self.current_task_idx = 0
        task = SQL_TASKS[self.current_task_idx]
        observation = SqlQueryObservation(
            question=task["question"],
            schema=task["schema"],
            difficulty=task["difficulty"],
            reward=0.0,
            done=False,
            feedback="Environment reset. Please solve the first task."
        )
        return observation, {"episode_id": "ep_0", "step_count": 0}

    def step(self, action: SqlQueryAction) -> Tuple[SqlQueryObservation, float, bool, Dict[str, Any]]:
        task = SQL_TASKS[self.current_task_idx]
        result = grade_query(action.sql_query, task, self.db)
        
        reward = result["score"]
        feedback = result["feedback"]
        
        # In this simple env, we move to next task or end
        self.current_task_idx += 1
        done = self.current_task_idx >= len(SQL_TASKS)
        
        if not done:
            next_task = SQL_TASKS[self.current_task_idx]
            observation = SqlQueryObservation(
                question=next_task["question"],
                schema=next_task["schema"],
                difficulty=next_task["difficulty"],
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
            
        return observation, reward, done, {"step_count": self.current_task_idx}
