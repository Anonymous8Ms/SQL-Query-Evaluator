import random
from server.grader import grade_query
from server.database import get_db_connection
from models import SqlQueryAction, SqlQueryObservation
from tasks import TASKS


class SqlQueryEnvironment:

    def __init__(self):
        self._db = get_db_connection()
        self._current_task = None

    def reset(self):
        self._current_task = random.choice(TASKS)

        return SqlQueryObservation(
            question=self._current_task["question"],
            schema=self._current_task["schema"],
            difficulty=self._current_task["difficulty"],
            reward=0.0,
            done=False,
            feedback=""
        )

    def step(self, action: SqlQueryAction):

        reward, feedback = grade_query(
            ai_query=action.sql_query,
            task=self._current_task,
            db_connection=self._db
        )

        return SqlQueryObservation(
            question=self._current_task["question"],
            schema=self._current_task["schema"],
            difficulty=self._current_task["difficulty"],
            reward=reward,
            done=True,
            feedback=feedback
        )