from openenv.core.env_server.http_server import create_app
from sql_query_env.models import SqlQueryAction, SqlQueryObservation
from sql_query_env.server.sql_query_env_environment import SqlQueryEnvironment

def main():
    return create_app(
        SqlQueryEnvironment,
        SqlQueryAction,
        SqlQueryObservation,
        env_name="sql_query_env"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(main(), host="0.0.0.0", port=8000)
