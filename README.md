# SQL Query Evaluator

This project is a SQL Query Evaluation environment built with OpenEnv.
It allows for interactive SQL query assessment and grading.

## Components
- **Client**: `sql_query_env/client.py` - Interacts with the environment.
- **Models**: `sql_query_env/models.py` - Defines data types with Pydantic.
- **Server**: `sql_query_env/server/` - Implementation of the environment and grading logic.
  - `grader.py`: Evaluates SQL queries against expected outputs.
  - `database.py`: Manages the in-memory SQLite database.
  - `app.py`: FastAPI server for the environment.

## Usage
To run the server locally:
```bash
python -m sql_query_env.server.app
```
