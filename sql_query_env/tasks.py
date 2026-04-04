TASKS = [
    {
        "id": 1,
        "difficulty": "easy",
        "question": "Count total number of customers",
        "schema": "customers(id, name)",
        "correct_output": [(10,)],
        "required_tables": ["customers"],
        "required_keywords": ["COUNT"]
    },
    {
        "id": 2,
        "difficulty": "medium",
        "question": "Find total orders per customer",
        "schema": "orders(id, customer_id)",
        "correct_output": [(1, 3), (2, 5)],
        "required_tables": ["orders"],
        "required_keywords": ["GROUP BY"]
    }
]