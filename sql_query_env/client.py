from openenv import Client
from .models import SqlQueryAction, SqlQueryObservation

class SqlQueryClient(Client):
    def _step_payload(self, action: SqlQueryAction):
        """Send the SQL query payload to the server."""
        return {"sql_query": action.sql_query}

    def _parse_result(self, result):
        """Parse server response into SqlQueryObservation."""
        obs = result.get("observation", {})
        return SqlQueryObservation(
            question=obs.get("question", ""),
            schema=obs.get("schema", ""),
            difficulty=obs.get("difficulty", ""),
            reward=result.get("reward", 0.0),
            done=result.get("done", False),
            feedback=obs.get("feedback", "")
        )

    def _parse_state(self, payload):
        """Return episode state metadata."""
        return {
            "episode_id": payload.get("episode_id"),
            "step_count": payload.get("step_count")
        }
