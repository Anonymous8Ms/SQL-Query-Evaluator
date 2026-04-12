from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import Optional, Any, Dict
import traceback

from sql_query_env.server.sql_query_env_environment import SqlQueryEnvironment
from sql_query_env.models import SqlQueryAction, SqlQueryObservation

app = FastAPI()

_env = None

def get_env():
    global _env
    if _env is None:
        _env = SqlQueryEnvironment()
    return _env

class ResetRequest(BaseModel):
    config: Optional[Dict[str, Any]] = None

class StepRequest(BaseModel):
    sql_query: str = ""

@app.get("/")
def root():
    return {"message": "Server is running"}

@app.post("/reset")
def reset(request: ResetRequest = None):
    try:
        env = get_env()
        config = request.config if request else None
        obs, info = env.reset(config=config)
        return {"observation": obs.model_dump(), "info": info}
    except Exception as e:
        return {"observation": {}, "info": {"error": str(e)}}

@app.post("/step")
def step(request: StepRequest):
    try:
        env = get_env()
        action = SqlQueryAction(sql_query=request.sql_query)
        obs, reward, done, info = env.step(action)
        return {"observation": obs.model_dump(), "reward": float(reward), "done": bool(done), "info": info}
    except Exception as e:
        return {"observation": {}, "reward": 0.0, "done": False, "info": {"error": str(e)}}

@app.get("/state")
def state():
    return {"state": {}}

def main():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
    )

if __name__ == "__main__":
    main()
