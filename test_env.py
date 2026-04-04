from server.sql_query_env_environment import SqlQueryEnvironment
from models import SQLAction

class DummyGrader:
    def evaluate(self, predicted_query, expected_query):
        if predicted_query.strip().lower() == expected_query.strip().lower():
            return 1.0, "Correct"
        return 0.0, "Incorrect"

env = SqlQueryEnvironment(grader=DummyGrader())

q = env.reset()
print("Question:", q)

action = SQLAction(query="SELECT * FROM users WHERE age > 30;")

obs = env.step(action)

print("Score:", obs.score)
print("Feedback:", obs.feedback)
print("Done:", obs.done)