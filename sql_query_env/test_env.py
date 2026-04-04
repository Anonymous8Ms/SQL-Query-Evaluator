from server.sql_query_env_environment import SqlQueryEnvironment
from models import SQLAction
from server.grader import SQLGrader

env = SqlQueryEnvironment(grader=SQLGrader())

q = env.reset()
print("Question:", q)

# Try a WRONG query to test properly
# action = SQLAction(query="SELECT name FROM users;")
# action = SQLAction(query="SELECT * FROM users WHERE age > 30;")
# action = SQLAction(query="SELECT name FROM users;")
action = SQLAction(query="SELECT * FROM random_table;")

obs = env.step(action)

print("Score:", obs.score)
print("Feedback:", obs.feedback)
print("Done:", obs.done)