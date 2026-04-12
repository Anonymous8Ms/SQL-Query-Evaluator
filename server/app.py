from fastapi import FastAPI
import uvicorn

from sql_query_env.server.sql_query_env_environment import SqlQueryEnvironment
from sql_query_env.models import SqlQueryAction

app = FastAPI()

env = SqlQueryEnvironment()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    obs, info = env.reset()
    return {
        "observation": obs.dict() if hasattr(obs, 'dict') else obs.model_dump(),
        "info": info
    }

@app.post("/step")
def step(data: dict):
    action = SqlQueryAction(sql_query=data.get("sql_query", ""))
    obs, reward, done, info = env.step(action)

    return {
        "observation": obs.dict() if hasattr(obs, 'dict') else obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state():
    return {"state": getattr(env, "state", lambda: {})()}

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
