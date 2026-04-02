import random
from models import SQLAction, SQLObservation
from tasks import TASKS

class SqlQueryEnvironment:
    def __init__(self, grader):
        self.grader = grader
        self.current_task = None
        self.attempts = 0

    def reset(self):
        self.current_task = random.choice(TASKS)
        self.attempts = 0
        return self.current_task["question"]

    def step(self, action: SQLAction):
        self.attempts += 1

        score, feedback = self.grader.evaluate(
            predicted_query=action.query,
            expected_query=self.current_task["expected_query"]
        )

        done = True

        return SQLObservation(
            score=score,
            feedback=feedback,
            done=done
        )

    def state(self):
        return {
            "task_id": self.current_task["id"],
            "difficulty": self.current_task["difficulty"],
            "attempts": self.attempts
        }