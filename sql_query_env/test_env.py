from sql_query_env.server.sql_query_env_environment import SqlQueryEnvironment
from sql_query_env.models import SqlQueryAction

env = SqlQueryEnvironment()
obs = env.reset()

print("Question:", obs.question)

action = SqlQueryAction(sql_query="SELECT * FROM customers WHERE city = 'Bengaluru'")
result = env.step(action)

print("Score:", result.reward)
print("Feedback:", result.feedback)
print("Done:", result.done)
