import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_SPACE_URL = os.getenv("HF_SPACE_URL")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

def run_episode():
    res = requests.get(f"{HF_SPACE_URL}/reset")
    data = res.json()

    done = False
    total_reward = 0

    while not done:
        question = data.get("question", "")

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": question}]
        )

        action = response.choices[0].message.content

        step_res = requests.get(f"{HF_SPACE_URL}/step", params={"action": action})
        step_data = step_res.json()

        reward = step_data.get("reward", 0)
        done = step_data.get("done", True)

        total_reward += reward
        data = step_data

    return total_reward


def main():
    scores = []

    for _ in range(10):
        score = run_episode()
        scores.append(score)

    avg_score = sum(scores) / len(scores)
    print("Average Score:", avg_score)


if __name__ == "__main__":
    main()
