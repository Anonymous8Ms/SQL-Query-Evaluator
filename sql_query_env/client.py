from openenv import Client
from .models import SqlQueryAction, SqlQueryObservation

class SqlQueryClient(Client):
    def _step_payload(self, action: SqlQueryAction):
        """Send the correct SQL query payload to the server."""
        return {"sql_query": action.sql_query}

    def _parse_result(self, result):
        """
        Parse the server response into a SqlQueryObservation.
        Extracts observation details and top-level reward/done status.
        """
        obs = result.get("observation", {})
        return SqlQueryObservation(
            question=obs.get("question", ""),
            schema=obs.get("schema", ""),
            difficulty=obs.get("difficulty", "easy"),
            reward=result.get("reward", 0.0),
            done=result.get("done", False),
            feedback=obs.get("feedback", "")
        )

    def _parse_state(self, payload):
        """Return basic episode metadata."""
        return {
            "episode_id": payload.get("episode_id"),
            "step_count": payload.get("step_count")
        }
