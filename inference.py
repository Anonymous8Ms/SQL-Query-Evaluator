import os
from openai import OpenAI

from sql_query_env.client import SqlQueryClient
from sql_query_env.models import SqlQueryAction

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_SPACE_URL = os.getenv("HF_SPACE_URL")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


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
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{"role": "user", "content": question}],
                    )
                    action = response.choices[0].message.content.strip()
                except Exception as exc:
                    print("LLM call failed:", exc)
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
    scores = []

    for i in range(10):
        print(f"Running episode {i + 1}")
        score = run_episode()
        scores.append(score)

    avg_score = sum(scores) / len(scores) if scores else 0.0
    print("Average Score:", avg_score)


if __name__ == "__main__":
    main()
