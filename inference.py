# ── Suppress ALL warnings FIRST — validator runs with -W error ───────────────
import warnings
warnings.filterwarnings("ignore")

import os
import sys
import json
import time
import random
import urllib.request
import urllib.error
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Environment variables (required by hackathon checklist) ───────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "<your-api-base-url>")
MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model>")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_SPACE_URL = os.getenv("HF_SPACE_URL", "").rstrip("/")
FALLBACK_MODEL_NAMES = os.getenv("FALLBACK_MODEL_NAMES", "")

openai_client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


# ── HTTP helpers (no sql_query_env import — avoids Pydantic schema warning) ───

def _http_post(url, payload=None, timeout=60):
    """POST JSON to url, return parsed dict. Raises RuntimeError on failure."""
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body[:300]}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Connection error: {exc.reason}")


def env_reset():
    """Reset the environment. Returns observation dict."""
    result = _http_post(f"{HF_SPACE_URL}/reset")
    return result.get("observation", {})


def env_step(sql_query):
    """Execute one step. Returns (observation_dict, reward, done)."""
    result = _http_post(f"{HF_SPACE_URL}/step", {"sql_query": sql_query})
    obs = result.get("observation", {})
    reward = float(result.get("reward", 0.0))
    done = bool(result.get("done", False))
    return obs, reward, done


# ── LLM helpers ───────────────────────────────────────────────────────────────

def get_candidate_models():
    models = []
    primary = (MODEL_NAME or "").strip()
    if primary:
        models.append(primary)
    for m in FALLBACK_MODEL_NAMES.split(","):
        m = m.strip()
        if m and m not in models:
            models.append(m)
    return models


def validate_configuration():
    missing = [
        name for name, val in (
            ("API_BASE_URL", API_BASE_URL),
            ("HF_TOKEN", HF_TOKEN),
            ("HF_SPACE_URL", HF_SPACE_URL),
        ) if not val
    ]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    if not get_candidate_models():
        raise ValueError("No model configured. Set MODEL_NAME or FALLBACK_MODEL_NAMES.")


def is_capacity_error(exc):
    msg = str(exc).lower()
    return any(k in msg for k in ("503", "capacity", "unavailable", "exhausted"))


def call_llm_with_retry(prompt, max_retries=5, base_delay=1.0, max_delay=60.0):
    models = get_candidate_models()
    last_cap_err = None
    for model_name in models:
        for attempt in range(max_retries):
            try:
                resp = openai_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.choices[0].message.content.strip()
            except Exception as exc:
                if is_capacity_error(exc):
                    last_cap_err = exc
                    if attempt < max_retries - 1:
                        delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                        print(f"Model {model_name} unavailable (attempt {attempt+1}/{max_retries}). Retry in {delay:.1f}s")
                        time.sleep(delay)
                        continue
                    print(f"Model {model_name} exhausted after {max_retries} attempts, trying next.")
                    break
                print(f"LLM error on {model_name}: {exc}")
                raise
    if last_cap_err:
        raise RuntimeError("All models unavailable.") from last_cap_err
    raise RuntimeError("No model call was attempted.")


def _clean_sql(raw):
    """Strip markdown fences and trailing semicolons from LLM output."""
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else parts[0]
        if raw.lower().startswith("sql"):
            raw = raw[3:]
    return raw.strip().split(";")[0].strip()


# ── Episode runner ────────────────────────────────────────────────────────────

def run_episode(episode_num: int) -> float:
    try:
        obs = env_reset()
        total_reward = 0.0
        step_num = 0

        print(f"[START] episode={episode_num}")

        while not obs.get("done", False):
            question = obs.get("question", "")
            if not question:
                print("No question received — ending episode.")
                break

            # HF Space returns "schema" key (old server), fall back gracefully
            db_schema = obs.get("db_schema", obs.get("schema", ""))

            prompt = (
                "Write ONLY a single SQL SELECT query with no explanation.\n"
                f"Question: {question}\n"
                f"Schema:\n{db_schema}"
            )

            try:
                raw_action = call_llm_with_retry(prompt)
                sql_query = _clean_sql(raw_action)
            except Exception as exc:
                print(f"LLM failed: {exc}")
                break

            try:
                obs, reward, done = env_step(sql_query)
                total_reward += reward
                step_num += 1
                is_correct = obs.get("is_correct", False)
                print(
                    f"[STEP] episode={episode_num} step={step_num} "
                    f"reward={reward:.4f} is_correct={is_correct} "
                    f"query={sql_query[:80]!r}"
                )
            except Exception as exc:
                print(f"Step failed: {exc}")
                break

        print(f"[END] episode={episode_num} total_reward={total_reward:.4f}")
        return total_reward

    except Exception as exc:
        print(f"[END] episode={episode_num} total_reward=0.0 error={exc}")
        return 0.0


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    try:
        validate_configuration()
    except ValueError as exc:
        print(f"Configuration Error: {exc}")
        print("Average Score: 0.0000")
        return

    scores = []
    try:
        for i in range(10):
            print(f"Running episode {i + 1}")
            score = run_episode(i + 1)
            scores.append(score)

        avg = sum(scores) / len(scores) if scores else 0.0
        print(f"Average Score: {avg:.4f}")
    except Exception as exc:
        print(f"Runtime Error: {exc}")
        print("Average Score: 0.0000")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as exc:
        print(f"FATAL: {exc}")
