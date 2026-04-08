---
title: SQL Query Env
emoji: "🗃️"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# SQL Query Evaluator

## Overview
This project is a SQL Query Evaluation Environment that allows users to submit SQL queries and receive automated scoring and feedback based on correctness and query quality.

It simulates a mini SQL judge system similar to platforms like LeetCode or HackerRank, specifically for SQL problems.

---

## Features

- Predefined SQL tasks with varying difficulty (easy, medium)
- Executes user queries on a SQLite database
- Compares output with expected results
- Provides:
  - Score (based on correctness and completeness)
  - Feedback (execution status, missing tables, keywords, etc.)
- Lightweight and modular design

---
## How It Works

1. The environment selects a predefined SQL task.
2. The user submits a SQL query.
3. The system:
   - Executes the query
   - Compares results with expected output
   - Evaluates query structure (tables, keywords)
4. Returns:
   - Score (0.0 – 1.0)
   - Feedback message

---

## Example Flow

Question:
Find all customers from Bengaluru

User Query:
SELECT * FROM customers WHERE city = 'Bengaluru'

Output:
Score: 1.0  
Feedback: Query executed successfully | Output matched  

---

## Installation & Setup

### 1. Clone Repository
git clone https://github.com/your-username/SQL-Query-Evaluator.git
cd SQL-Query-Evaluator

### 2. Install Dependencies
pip3 install -r requirements.txt

### 3. Configure Inference
Set these environment variables before running `inference.py`:

- `API_BASE_URL`: OpenAI-compatible inference endpoint
- `HF_TOKEN`: API key / bearer token for that endpoint
- `HF_SPACE_URL`: URL for the SQL environment service
- `MODEL_NAME`: primary model name
- `FALLBACK_MODEL_NAMES`: optional comma-separated fallback models used when the primary model returns `503` or capacity errors

Example:

```bash
export API_BASE_URL="https://your-inference-endpoint/v1"
export HF_TOKEN="your-token"
export HF_SPACE_URL="https://your-space-url"
export MODEL_NAME="claude-sonnet-4-6"
export FALLBACK_MODEL_NAMES="gpt-4.1-mini,meta-llama-3.1-70b-instruct"
```

## Running the Project
python3 -m sql_query_env.test_env
Question: List products ordered by customer with ID 1
Score: 0.15
Feedback: Query executed successfully | No match | Missing tables | Missing keywords
Done: True


---

## Technologies Used

- Python 3
- SQLite
- Pydantic

---

## Notes

- SQL tasks are predefined in `tasks.py`
- The system evaluates both correctness and query structure
- Warning related to `schema` field can be safely ignored

---

## Future Improvements

- Add more SQL tasks
- Improve scoring logic
- Add UI (Gradio / Web)
- Deploy as API

---
