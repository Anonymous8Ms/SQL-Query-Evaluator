"""
Self-contained FastAPI server for the SQL Query Environment.
Exposes /reset, /step, /health endpoints required by the OpenEnv validator.
No dependency on openenv-core at runtime — works standalone on Hugging Face Spaces.
"""
import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict

from sql_query_env.models import SqlQueryAction, SqlQueryObservation
from sql_query_env.server.sql_query_env_environment import SqlQueryEnvironment
from sql_query_env.server.database import get_db_connection

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SQL Query Environment",
    description="OpenEnv-compatible SQL evaluation environment.",
    version="1.0.0",
)

# ── Singleton environment instance ────────────────────────────────────────────
_env: Optional[SqlQueryEnvironment] = None


def get_env() -> SqlQueryEnvironment:
    global _env
    if _env is None:
        _env = SqlQueryEnvironment()
    return _env


# ── Request / Response structures ─────────────────────────────────────────────────
class ResetRequest(BaseModel):
    config: Optional[Dict[str, Any]] = None


class StepRequest(BaseModel):
    sql_query: str = ""


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "sql_query_env", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/reset")
def reset(request: ResetRequest = None):
    """Reset the environment and return the first observation."""
    try:
        env = get_env()
        obs, info = env.reset(config=request.config if request else None)
        return {
            "observation": obs.model_dump(),
            "info": info,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/step")
def step(request: StepRequest):
    """Execute one step and return observation, reward, done."""
    try:
        env = get_env()
        action = SqlQueryAction(sql_query=request.sql_query)
        obs, reward, done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": float(reward),
            "done": bool(done),
            "info": info,
        }
    except RuntimeError as exc:
        # Environment not reset yet
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/state")
def state():
    return {"state": {}}


# ── Optional openenv-core integration (does NOT break if missing) ─────────────
try:
    from openenv.core.env_server import create_app as _create_app  # type: ignore
    _openenv_app = _create_app(
        SqlQueryEnvironment,
        SqlQueryAction,
        SqlQueryObservation,
        env_name="sql_query_env",
        max_concurrent_envs=1,
    )
    # Mount openenv routes without overriding our explicit endpoints
except Exception:
    pass  # openenv-core not available — our explicit endpoints handle everything


import uvicorn

def main():
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=7860,
        reload=False
    )

if __name__ == "__main__":
    main()
