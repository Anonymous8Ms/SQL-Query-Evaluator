from fastapi import FastAPI

from models import SqlQueryAction, SqlQueryObservation
from server.sql_query_env_environment import SqlQueryEnvironment

try:
    from openenv.core.env_server import create_app
except ImportError:  # pragma: no cover - allow the Space to boot without openenv-core
    create_app = None


def create_fallback_app() -> FastAPI:
    fallback_app = FastAPI(
        title="SQL Query Environment",
        description="Fallback server for environments where openenv-core is unavailable.",
    )

    @fallback_app.get("/")
    def root():
        return {"status": "ok", "service": "sql_query_env", "docs": "/docs"}

    @fallback_app.get("/health")
    def health():
        return {"status": "healthy"}

    return fallback_app


if create_app is not None:
    app = create_app(
        SqlQueryEnvironment,
        SqlQueryAction,
        SqlQueryObservation,
        env_name="sql_query_env",
        max_concurrent_envs=1,
    )

    @app.get("/")
    def root():
        return {"status": "ok", "service": "sql_query_env", "docs": "/docs"}

    @app.get("/health")
    def health():
        return {"status": "healthy"}
else:
    app = create_fallback_app()


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)

