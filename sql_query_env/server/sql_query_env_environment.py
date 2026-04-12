from __future__ import annotations
from typing import Any

try:
    from openenv.core.env_server import Env
except ImportError:  # pragma: no cover - allow local testing without openenv-core
    class Env:
        pass

from sql_query_env.models import SqlQueryAction, SqlQueryObservation
from sql_query_env.tasks import SQL_TASKS
from sql_query_env.server.database import get_db_connection
from sql_query_env.server.grader import grade_query


class SqlQueryEnvironment(Env):
    def __init__(self):
        super().__init__()
        self._db = get_db_connection()
        self._task_idx = 0
        self._current_task = None

    def reset(self, config: dict[str, Any] | None = None):
        self._task_idx = 0
        self._current_task = SQL_TASKS[self._task_idx]

        observation = SqlQueryObservation(
            task_id=self._current_task["id"],
            question=self._current_task["question"],
            db_schema=self._current_task["db_schema"],
            difficulty=self._current_task["difficulty"],
            reward=0.0,
            done=False,
            feedback="Environment reset. Solve the first task.",
        )
        return observation, {"episode_id": "ep_0", "step_count": 0}

    def step(self, action: SqlQueryAction):
        if self._current_task is None:
            raise RuntimeError("Environment must be reset before calling step().")

        result = grade_query(
            ai_query=action.sql_query,
            task=self._current_task,
            db_connection=self._db,
        )

        reward = result["score"]
        feedback = result["feedback"]

        self._task_idx += 1
        done = self._task_idx >= len(SQL_TASKS)

        if not done:
            self._current_task = SQL_TASKS[self._task_idx]
            observation = SqlQueryObservation(
                task_id=self._current_task["id"],
                question=self._current_task["question"],
                db_schema=self._current_task["db_schema"],
                difficulty=self._current_task["difficulty"],
                reward=reward,
                done=False,
                feedback=feedback,
            )
        else:
            self._current_task = None
            observation = SqlQueryObservation(
                task_id=0,
                question="No more tasks.",
                db_schema="",
                difficulty="",
                reward=reward,
                done=True,
                feedback=feedback,
            )

        return observation, reward, done, {"step_count": self._task_idx}
