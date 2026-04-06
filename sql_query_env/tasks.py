SQL_TASKS = [
    {
        "id": 1,
        "question": "Select all customers from Bengaluru",
        "difficulty": "easy",
        "schema": "customers(id, name, city, email)",
        "expected_query": "SELECT * FROM customers WHERE city = 'Bengaluru'",
        "correct_output": [(1, "Anuttama", "Bengaluru", "a@email.com")],
        "required_tables": ["customers"],
        "required_keywords": ["SELECT", "WHERE"]
    },
    {
        "id": 2,
        "question": "List all products in the Accessories category",
        "difficulty": "easy",
        "schema": "products(id, name, price, category)",
        "expected_query": "SELECT * FROM products WHERE category = 'Accessories'",
        "correct_output": [(2, "Mouse", 800, "Accessories"), (3, "Keyboard", 2200, "Accessories")],
        "required_tables": ["products"],
        "required_keywords": ["SELECT", "WHERE"]
    },
    {
        "id": 3,
        "question": "Find the total number of orders",
        "difficulty": "easy",
        "schema": "orders(id, customer_id, total, date)",
        "expected_query": "SELECT COUNT(*) FROM orders",
        "correct_output": [(4,)],
        "required_tables": ["orders"],
        "required_keywords": ["COUNT"]
    },
    {
        "id": 4,
        "question": "Get names of customers who placed an order on 2026-01-15",
        "difficulty": "medium",
        "schema": "customers(id, name), orders(customer_id, date)",
        "expected_query": "SELECT name FROM customers JOIN orders ON customers.id = orders.customer_id WHERE date = '2026-01-15'",
        "correct_output": [("Rahul",)],
        "required_tables": ["customers", "orders"],
        "required_keywords": ["JOIN", "WHERE"]
    },
    {
        "id": 5,
        "question": "List products ordered by customer with ID 1",
        "difficulty": "medium",
        "schema": "products(name), order_items(product_id), orders(id, customer_id)",
        "expected_query": "SELECT p.name FROM products p JOIN order_items oi ON p.id = oi.product_id JOIN orders o ON oi.order_id = o.id WHERE o.customer_id = 1",
        "correct_output": [("Keyboard",), ("Mouse",), ("Monitor",)],
        "required_tables": ["products", "order_items", "orders"],
        "required_keywords": ["JOIN", "WHERE"]
    }
]
