from openenv import Client
from models import SqlQueryAction, SqlQueryObservation

class SqlQueryClient(Client):
    def _step_payload(self, action: SqlQueryAction):
        return {"sql_query": action.sql_query}

    def _parse_result(self, result):
        obs = result["observation"]
        return SqlQueryObservation(
            question=obs.get("question"),
            schema=obs.get("schema"),
            difficulty=obs.get("difficulty"),
            feedback=obs.get("feedback")
        )

    def _parse_state(self, payload):
        return {
            "episode_id": payload.get("episode_id"),
            "step_count": payload.get("step_count")
        }
