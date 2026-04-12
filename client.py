try:
    from openenv.core.env_client import EnvClient
except ImportError:  # pragma: no cover - compatibility with older OpenEnv releases
    from openenv import Client as EnvClient

from models import SqlQueryAction, SqlQueryObservation


class SqlQueryClient(EnvClient):
    def _step_payload(self, action: SqlQueryAction | str):
        if isinstance(action, SqlQueryAction):
            return {"sql_query": action.sql_query}
        return {"sql_query": str(action)}

    def _parse_result(self, result):
        obs = result.get("observation", {})
        return SqlQueryObservation(
            question=obs.get("question", ""),
            db_schema=obs.get("db_schema", obs.get("schema", "")),
            difficulty=obs.get("difficulty", ""),
            reward=result.get("reward", 0.0),
            done=result.get("done", False),
            feedback=obs.get("feedback", ""),
        )

    def _parse_state(self, payload):
        return {
            "episode_id": payload.get("episode_id"),
            "step_count": payload.get("step_count"),
        }

