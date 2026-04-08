import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sql_query_env.models import SqlQueryAction
from sql_query_env.server.sql_query_env_environment import SqlQueryEnvironment


env = SqlQueryEnvironment()
obs, state = env.reset()

print("Question:", obs.question)
print("State:", state)

action = SqlQueryAction(sql_query="SELECT * FROM customers WHERE city = 'Bengaluru'")
obs, reward, done, info = env.step(action)

print("Score:", reward)
print("Feedback:", obs.feedback)
print("Done:", done)
print("Info:", info)
