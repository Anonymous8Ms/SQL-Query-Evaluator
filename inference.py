import os
from openai import OpenAI
from sql_query_env.client import SqlQueryEnv

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_SPACE_URL = os.getenv("HF_SPACE_URL")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


def run_episode():
    try:
        env = SqlQueryEnv(base_url=HF_SPACE_URL)
        result = env.reset()
        data = result.observation
    except Exception as e:
        print("Reset failed:", e)
        return 0

    done = False
    total_reward = 0

    while not done:
        question = data.get("question")

        if not question:
            print("No question received")
            break

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": question}]
            )
            action = response.choices[0].message.content.strip()
        except Exception as e:
            print("LLM call failed:", e)
            break

        try:
            result = env.step(action)
            data = result.observation
            reward = result.reward
            done = result.done
        except Exception as e:
            print("Step failed:", e)
            break

        total_reward += reward

    return total_reward


def main():
    scores = []

    for i in range(10):
        print(f"Running episode {i+1}")
        score = run_episode()
        scores.append(score)

    avg_score = sum(scores) / len(scores)
    print("Average Score:", avg_score)


if __name__ == "__main__":
    main()
