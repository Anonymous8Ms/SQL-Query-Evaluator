# ── MUST BE FIRST: suppress ALL warnings before any import ──────────────────
# The validator runs Python with -W error, converting UserWarnings to exceptions.
# Pydantic can emit a UserWarning about "schema" shadowing during class definition.
# Suppressing here prevents that warning from crashing inference.py.
import warnings
warnings.filterwarnings("ignore")

import os
import sys
import importlib

# Force local sql_query_env to load before any version installed by openenv-core.
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

# Bust stale module cache so openenv-core's installed sql_query_env is not reused.
importlib.invalidate_caches()
for _mod in list(sys.modules.keys()):
    if _mod.startswith("sql_query_env"):
        del sys.modules[_mod]

import time
import random
from openai import OpenAI
from dotenv import load_dotenv

from sql_query_env.client import SqlQueryClient
from sql_query_env.models import SqlQueryAction

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_SPACE_URL = os.getenv("HF_SPACE_URL")
FALLBACK_MODEL_NAMES = os.getenv("FALLBACK_MODEL_NAMES", "")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


def get_candidate_models():
    models = []
    primary_model = (MODEL_NAME or "").strip()
    if primary_model:
        models.append(primary_model)

    for model in FALLBACK_MODEL_NAMES.split(","):
        cleaned = model.strip()
        if cleaned and cleaned not in models:
            models.append(cleaned)

    return models


def validate_configuration():
    missing = [
        name
        for name, value in (
            ("API_BASE_URL", API_BASE_URL),
            ("HF_TOKEN", HF_TOKEN),
            ("HF_SPACE_URL", HF_SPACE_URL),
        )
        if not value
    ]

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    if not get_candidate_models():
        raise ValueError(
            "No model configured. Set MODEL_NAME or MODEL_NAME with FALLBACK_MODEL_NAMES."
        )


def is_capacity_error(exc):
    error_msg = str(exc).lower()
    return (
        "503" in error_msg
        or "capacity" in error_msg
        or "unavailable" in error_msg
        or "exhausted" in error_msg
    )


def call_llm_with_retry(question, max_retries=5, base_delay=1.0, max_delay=60.0):
    """
    Call the LLM and fall back across candidate models when capacity is exhausted.
    """
    models = get_candidate_models()
    last_capacity_error = None

    for model_name in models:
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": question}],
                )
                return response.choices[0].message.content.strip()

            except Exception as exc:
                if is_capacity_error(exc):
                    last_capacity_error = exc
                    if attempt < max_retries - 1:
                        delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                        print(
                            f"Model {model_name} unavailable "
                            f"(attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {delay:.1f} seconds..."
                        )
                        time.sleep(delay)
                        continue

                    print(
                        f"Model {model_name} remained unavailable after {max_retries} attempts. "
                        "Trying the next configured model..."
                    )
                    break

                print(f"LLM call failed with unexpected error on model {model_name}: {exc}")
                raise

    if last_capacity_error is not None:
        raise RuntimeError(
            "All configured models are unavailable. "
            "Update MODEL_NAME / FALLBACK_MODEL_NAMES to models with available capacity."
        ) from last_capacity_error

    raise RuntimeError("No model call was attempted.")


def run_episode():
    try:
        with SqlQueryClient(base_url=HF_SPACE_URL).sync() as env:
            result = env.reset()
            data = result.observation
            total_reward = 0.0

            while not data.done:
                question = data.question
                if not question:
                    print("No question received")
                    break

                try:
                    action = call_llm_with_retry(question)
                except Exception as exc:
                    print("LLM call failed after retries:", exc)
                    break

                try:
                    result = env.step(SqlQueryAction(sql_query=action))
                    data = result.observation
                    total_reward += result.reward
                except Exception as exc:
                    print("Step failed:", exc)
                    break

            return total_reward
    except Exception as exc:
        print("Reset failed:", exc)
        return 0.0


def main():
    try:
        validate_configuration()
    except ValueError as exc:
        print(f"Configuration Error: {exc}")
        return

    scores = []
    try:
        for i in range(10):
            print(f"Running episode {i + 1}")
            score = run_episode()
            scores.append(score)

        avg_score = sum(scores) / len(scores) if scores else 0.0
        print(f"Average Score: {avg_score:.2f}")
    except Exception as exc:
        print(f"Runtime Error: {exc}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as exc:
        print(f"FATAL: Unhandled exception: {exc}")
