from sql_query_env.server.sql_query_env_environment import SqlQueryEnvironment
from sql_query_env.models import SQLAction

env = SqlQueryEnvironment()

obs = env.reset()
print("Question:", obs.question)

action = SQLAction(sql_query="SELECT * FROM customers")

result = env.step(action)

print("Score:", result.reward)
print("Feedback:", result.feedback)
print("Done:", result.done)
