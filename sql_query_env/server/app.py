from openenv.core.env_server import create_app
from .sql_query_env_environment import SqlQueryEnvironment
from ..models import SqlQueryAction, SqlQueryObservation

app = create_app(
    SqlQueryEnvironment,
    SqlQueryAction,
    SqlQueryObservation,
    env_name="sql_query_env",
    max_concurrent_envs=1,
)

def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)
