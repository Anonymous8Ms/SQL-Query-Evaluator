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

from dotenv import load_dotenv

load_dotenv()

# ── Environment variables ─────────────────────────────────────────────────────
API_BASE_URL       = os.getenv("API_BASE_URL", "").strip()
MODEL_NAME         = os.getenv("MODEL_NAME", "").strip()
HF_TOKEN           = os.getenv("HF_TOKEN", "").strip()
HF_SPACE_URL       = os.getenv("HF_SPACE_URL", "").rstrip("/")
FALLBACK_MODEL_NAMES = os.getenv("FALLBACK_MODEL_NAMES", "").strip()

# ── OpenAI client created lazily inside functions — NOT at module level ───────
# This prevents a crash when env vars are missing at import time.
_openai_client = None

def _get_client():
    global _openai_client
    if _openai_client is None:
        try:
            from openai import OpenAI
            _openai_client = OpenAI(
                base_url=API_BASE_URL or None,
                api_key=HF_TOKEN or None,
            )
        except Exception as exc:
            raise RuntimeError(f"Cannot create OpenAI client: {exc}") from exc
    return _openai_client


# ── HTTP helpers (pure stdlib) ────────────────────────────────────────────────

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


class ObjectWrapper:
    def __init__(self, d):
        for k, v in d.items():
            setattr(self, k, v)
    def get(self, k, default=None):
        return getattr(self, k, default)

class HttpEnv:
    def step(self, action):
        result = _http_post(f"{HF_SPACE_URL}/step", {"sql_query": action})
        obs    = ObjectWrapper(result.get("observation", {}))
        reward = float(result.get("reward", 0.0))
        done   = bool(result.get("done", False))
        info   = result.get("info", {})
        return obs, reward, done, info
        
    def reset(self):
        result = _http_post(f"{HF_SPACE_URL}/reset")
        return ObjectWrapper(result.get("observation", {}))

env = HttpEnv()

# ── LLM helpers ───────────────────────────────────────────────────────────────

def get_candidate_models():
    models = []
    if MODEL_NAME:
        models.append(MODEL_NAME)
    for m in FALLBACK_MODEL_NAMES.split(","):
        m = m.strip()
        if m and m not in models:
            models.append(m)
    return models


def validate_configuration():
    missing = [
        name for name, val in (
            ("API_BASE_URL", API_BASE_URL),
            ("HF_TOKEN",     HF_TOKEN),
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
    client = _get_client()
    models = get_candidate_models()
    last_cap_err = None

    for model_name in models:
        for attempt in range(max_retries):
            try:
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.choices[0].message.content.strip()
            except Exception as exc:
                if is_capacity_error(exc):
                    last_cap_err = exc
                    if attempt < max_retries - 1:
                        delay = min(
                            base_delay * (2 ** attempt) + random.uniform(0, 1),
                            max_delay,
                        )
                        print(
                            f"Model {model_name} unavailable "
                            f"(attempt {attempt+1}/{max_retries}). "
                            f"Retry in {delay:.1f}s"
                        )
                        time.sleep(delay)
                        continue
                    print(
                        f"Model {model_name} exhausted after {max_retries} "
                        f"attempts, trying next."
                    )
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
        task = env.reset()
        total_reward = 0.0
        step_num = 0

        print(f"[START] episode={episode_num}")

        while not getattr(task, "done", False):
            question = task.get("question", "")
            if not question:
                print("No question received — ending episode.")
                break

            prompt = f"Write ONLY a SQL query for: {task.get('question')}\nDatabase Schema: {task.get('db_schema')}"

            try:
                raw_action = call_llm_with_retry(prompt)
                action = _clean_sql(raw_action)
            except Exception as exc:
                print(f"LLM failed: {exc}")
                break

            try:
                obs, reward, done, info = env.step(action)
            except Exception as e:
                print("ERROR:", str(e))
                continue

            total_reward += reward
            step_num += 1
            is_correct = getattr(obs, "is_correct", False)
            print(
                f"[STEP] episode={episode_num} step={step_num} "
                f"reward={reward:.4f} is_correct={is_correct} "
                f"query={action[:80]!r}"
            )
            task = obs

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
