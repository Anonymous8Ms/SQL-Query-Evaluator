# SQL-Query-Evaluator

# SQL Query Evaluator — OpenEnv Environment

> A reinforcement learning environment that trains AI agents to convert plain English questions into correct SQL queries — built on Meta's OpenEnv framework.

---

## What This Project Does

Natural language to SQL conversion (Text-to-SQL) is one of the most practically valuable AI skills — every company with a database needs it. This environment provides a structured training ground where an AI agent receives an English question, writes a SQL query, and receives a reward score based on how correct and well-formed that query is.

The environment mirrors real-world database query workflows using a simulated e-commerce dataset with customers, orders, products, and order items.

---

## Built With

| Tool | Purpose |
|---|---|
| [OpenEnv](https://github.com/meta-pytorch/OpenEnv) | RL environment framework by Meta + Hugging Face |
| Python 3.11 | Core language |
| SQLite | In-memory database for query execution |
| FastAPI | HTTP and WebSocket server |
| Pydantic | Type-safe action and observation models |
| Docker | Containerised deployment |
| Hugging Face Spaces | Live cloud deployment |

---

## Project Structure

```
sql_query_env/
├── models.py                          # Action and Observation definitions
├── tasks.py                           # Task bank — 15 SQL questions (easy/medium/hard)
├── client.py                          # OpenEnv client for connecting to the environment
├── openenv.yaml                       # Environment configuration
├── pyproject.toml                     # Python dependencies
├── test_env.py                        # Local test script
└── server/
    ├── app.py                         # FastAPI server (OpenEnv spec)
    ├── sql_query_env_environment.py   # Core environment logic (reset/step/state)
    ├── grader.py                      # Scoring and reward logic
    ├── database.py                    # SQLite database setup and sample data
    ├── requirements.txt               # Server dependencies
    └── Dockerfile                     # Container definition

inference.py                           # Baseline agent script (required for submission)
Dockerfile                             # Root deployment Dockerfile
requirements.txt                       # Root dependencies
README.md                              # This file
```

---

## The Database

The environment uses a fixed in-memory SQLite database with four tables representing a simple e-commerce shop.

**customers**

| id | name | city | email |
|---|---|---|---|
| 1 | Ankitha | Bengaluru | a@email.com |
| 2 | Rahul | Mumbai | r@email.com |
| 3 | Priya | Delhi | p@email.com |

**products**

| id | name | price | category |
|---|---|---|---|
| 1 | Laptop | 55000 | Electronics |
| 2 | Mouse | 800 | Accessories |
| 3 | Keyboard | 2200 | Accessories |
| 4 | Monitor | 18000 | Electronics |

**orders**

| id | customer_id | total | date |
|---|---|---|---|
| 1 | 2 | 6800 | 2026-01-15 |
| 2 | 1 | 3200 | 2026-01-22 |
| 3 | 3 | 1200 | 2026-02-10 |
| 4 | 1 | 1800 | 2026-02-14 |

**order_items**

| order_id | product_id | quantity |
|---|---|---|
| 1 | 1 | 1 |
| 1 | 2 | 2 |
| 2 | 3 | 1 |
| 2 | 2 | 1 |
| 3 | 2 | 1 |
| 4 | 4 | 1 |

---

## Action and Observation Spaces

### Action — what the agent sends

```python
class SqlQueryAction(Action):
    sql_query: str  # The SQL query the agent has written
```

### Observation — what the agent receives

```python
class SqlQueryObservation(Observation):
    question:   str    # The English question to convert to SQL
    schema:     str    # Relevant table structure for this question
    difficulty: str    # "easy", "medium", or "hard"
    reward:     float  # Score from the grader (0.0 to 1.0)
    done:       bool   # Whether the episode has ended
    feedback:   str    # Explanation of what was right or wrong
```

---

## Task Difficulty Levels

The environment has 15 tasks across three difficulty levels. Each level caps the maximum achievable reward to reflect the complexity of the task.

### Easy — max reward 0.3

Single-table queries using basic SQL operations: `SELECT`, `COUNT`, `MAX`, `WHERE`.

Example:
> "How many customers do we have?"
> Expected: `SELECT COUNT(*) FROM customers;`

### Medium — max reward 0.6

Multi-table queries requiring `JOIN` and `WHERE` conditions across two tables.

Example:
> "Which customers placed orders above ₹5000? Show their names."
> Expected: `SELECT customers.name FROM customers JOIN orders ON customers.id = orders.customer_id WHERE orders.total > 5000;`

### Hard — max reward 1.0

Complex queries requiring `GROUP BY`, `ORDER BY`, `LIMIT`, subqueries, or `NOT IN` logic across three or more tables.

Example:
> "Find the top 3 customers by total spending and show their city."
> Expected: `SELECT c.name, c.city, SUM(o.total) AS total_spent FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id ORDER BY total_spent DESC LIMIT 3;`

---

## Reward Function

The grader evaluates every SQL query on four criteria and gives partial credit for each:

| Check | Points (% of max) | Description |
|---|---|---|
| Query executes | 20% | Does the SQL run without an error? |
| Output matches | 50% | Does the result match the expected answer? (25% for partial match) |
| Correct tables used | 20% | Are the required tables referenced in the query? |
| Correct keywords used | 10% | Are required SQL keywords present? |

**Partial credit example:** An agent that writes a query referencing the right tables and using the right keywords, but getting the wrong output, will still score ~30% of the maximum — encouraging progressive learning rather than all-or-nothing scoring.

---

## API Endpoints

The environment exposes a standard OpenEnv interface over WebSocket and HTTP.

### `POST /reset`

Starts a new episode. Returns a new question with its schema and difficulty level.

```json
{
  "observation": {
    "question": "How many customers do we have?",
    "schema": "customers(id, name, city, email)",
    "difficulty": "easy",
    "reward": 0.0,
    "done": false,
    "feedback": "New task started. Write your SQL query."
  }
}
```

### `POST /step`

Submits a SQL query and returns the graded result.

Request body:
```json
{
  "sql_query": "SELECT COUNT(*) FROM customers;"
}
```

Response:
```json
{
  "observation": {
    "question": "How many customers do we have?",
    "schema": "customers(id, name, city, email)",
    "difficulty": "easy",
    "reward": 0.3,
    "done": true,
    "feedback": "Query ran successfully. | Output matched. | Used 1/1 required tables. | Used 1/1 required keywords."
  },
  "reward": 0.3,
  "done": true
}
```

### `GET /state`

Returns the current episode state.

```json
{
  "episode_id": "abc-123-...",
  "step_count": 1
}
```

---

## Setup and Local Development

### Prerequisites

- Python 3.10, 3.11, or 3.12
- [uv](https://docs.astral.sh/uv/) package manager
- Docker Desktop (for container testing)
- Hugging Face account (for deployment)

### Install and run locally

```bash
# Clone the repo
git clone https://github.com/Anonymous8Ms/SQL-Query-Evaluator.git
cd SQL-Query-Evaluator/sql_query_env

# Install dependencies
uv sync

# Run the server locally
uv run server
# Server starts at http://localhost:8000
```

### Test the environment locally

```bash
# Quick sanity check
uv run python -c "
from server.database import get_db_connection
from server.grader import grade_query
print('Database OK:', get_db_connection())
"

# Run the test script
uv run python test_env.py
```

### Build and run with Docker

```bash
# From the root of the repo
docker build -t sql-query-evaluator .
docker run -p 7860:7860 sql-query-evaluator

# Visit http://localhost:7860
```

---

## Deployment to Hugging Face Spaces

```bash
# Login to Hugging Face
huggingface-cli login

# Deploy using OpenEnv CLI
cd sql_query_env
openenv push
```

Or push manually:

```bash
git remote add hf https://huggingface.co/spaces/YOURNAME/sql-query-evaluator
git push hf main
```

Set the following environment variables in your Space settings:

| Variable | Description |
|---|---|
| `API_BASE_URL` | LLM API endpoint (e.g. `https://api-inference.huggingface.co/v1`) |
| `MODEL_NAME` | Model identifier (e.g. `mistralai/Mistral-7B-Instruct-v0.3`) |
| `HF_TOKEN` | Your Hugging Face access token |
| `HF_SPACE_URL` | Your deployed Space URL |

---

## Running the Baseline Inference Script

```bash
# Set environment variables first
export API_BASE_URL="https://api-inference.huggingface.co/v1"
export MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.3"
export HF_TOKEN="your_token_here"
export HF_SPACE_URL="https://yourname-sql-query-evaluator.hf.space"

# Run
python inference.py
```

Expected output:
```
Episode 1 | Difficulty: easy | Score: 0.30
Episode 2 | Difficulty: hard | Score: 0.60
...
Average score: 0.47
```

---

## Pre-Submission Checklist

Before submitting the Hugging Face Space URL on the dashboard:

- HF Space URL is public and returns 200
- `reset()` returns a question, schema, and difficulty
- `step()` returns a reward between 0.0 and 1.0
- All 3 difficulty levels are reachable
- `inference.py` runs end to end in under 20 minutes
- `openenv.yaml` is present and valid
- Dockerfile builds and runs without errors
- README documents action/observation spaces clearly

---
