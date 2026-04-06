import random
from sql_query_env.tasks import SQL_TASKS
from sql_query_env.models import SqlQueryObservation
from sql_query_env.server.grader import grade_query
from sql_query_env.server.database import get_db_connection


class SqlQueryEnvironment:
    def __init__(self):
        self.db = get_db_connection()
        self.current_task = None

    def reset(self):
        self.current_task = random.choice(SQL_TASKS)

        return SqlQueryObservation(
            question=self.current_task["question"],
            schema=self.current_task["schema"],
            difficulty=self.current_task["difficulty"],
            reward=0.0,
            done=False,
            feedback=""
        )

    def step(self, action):
        result = grade_query(
            ai_query=action.sql_query,
            task=self.current_task,
            db_connection=self.db
        )

        score = result["score"]
        feedback = result["feedback"]

        return SqlQueryObservation(
            question=self.current_task["question"],
            schema=self.current_task["schema"],
            difficulty=self.current_task["difficulty"],
            reward=score,
            done=True,
            feedback=feedback
        )
