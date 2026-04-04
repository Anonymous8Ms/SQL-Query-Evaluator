TASKS = [
    # EASY
    {
        "id": 1,
        "question": "Count total customers",
        "difficulty": "easy",
        "schema": "customers(id, name)",
        "expected_query": "SELECT COUNT(*) FROM customers",
        "correct_output": [],
        "required_tables": ["customers"],
        "required_keywords": ["COUNT"]
    },
    {
        "id": 2,
        "question": "Get all customers",
        "difficulty": "easy",
        "schema": "customers(id, name)",
        "expected_query": "SELECT * FROM customers",
        "correct_output": [],
        "required_tables": ["customers"],
        "required_keywords": ["SELECT"]
    },
    {
        "id": 3,
        "question": "Get all products",
        "difficulty": "easy",
        "schema": "products(id, name, price)",
        "expected_query": "SELECT * FROM products",
        "correct_output": [],
        "required_tables": ["products"],
        "required_keywords": ["SELECT"]
    },
    {
        "id": 4,
        "question": "Find max product price",
        "difficulty": "easy",
        "schema": "products(id, name, price)",
        "expected_query": "SELECT MAX(price) FROM products",
        "correct_output": [],
        "required_tables": ["products"],
        "required_keywords": ["MAX"]
    },
    {
        "id": 5,
        "question": "Find min product price",
        "difficulty": "easy",
        "schema": "products(id, name, price)",
        "expected_query": "SELECT MIN(price) FROM products",
        "correct_output": [],
        "required_tables": ["products"],
        "required_keywords": ["MIN"]
    },

    # MEDIUM
    {
        "id": 6,
        "question": "Get all orders with customer names",
        "difficulty": "medium",
        "schema": "orders, customers",
        "expected_query": "SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id",
        "correct_output": [],
        "required_tables": ["orders", "customers"],
        "required_keywords": ["JOIN"]
    },
    {
        "id": 7,
        "question": "Get products with price > 100",
        "difficulty": "medium",
        "schema": "products(id, name, price)",
        "expected_query": "SELECT * FROM products WHERE price > 100",
        "correct_output": [],
        "required_tables": ["products"],
        "required_keywords": ["WHERE"]
    },
    {
        "id": 8,
        "question": "Get orders for customer_id = 1",
        "difficulty": "medium",
        "schema": "orders(id, customer_id)",
        "expected_query": "SELECT * FROM orders WHERE customer_id = 1",
        "correct_output": [],
        "required_tables": ["orders"],
        "required_keywords": ["WHERE"]
    },
    {
        "id": 9,
        "question": "Join order_items with products",
        "difficulty": "medium",
        "schema": "order_items, products",
        "expected_query": "SELECT * FROM order_items JOIN products ON order_items.product_id = products.id",
        "correct_output": [],
        "required_tables": ["order_items", "products"],
        "required_keywords": ["JOIN"]
    },
    {
        "id": 10,
        "question": "Get total number of orders",
        "difficulty": "medium",
        "schema": "orders(id)",
        "expected_query": "SELECT COUNT(*) FROM orders",
        "correct_output": [],
        "required_tables": ["orders"],
        "required_keywords": ["COUNT"]
    },

    # HARD
    {
        "id": 11,
        "question": "Count orders per customer",
        "difficulty": "hard",
        "schema": "orders(customer_id)",
        "expected_query": "SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id",
        "correct_output": [],
        "required_tables": ["orders"],
        "required_keywords": ["GROUP BY"]
    },
    {
        "id": 12,
        "question": "Get top 5 expensive products",
        "difficulty": "hard",
        "schema": "products(price)",
        "expected_query": "SELECT * FROM products ORDER BY price DESC LIMIT 5",
        "correct_output": [],
        "required_tables": ["products"],
        "required_keywords": ["ORDER BY", "LIMIT"]
    },
    {
        "id": 13,
        "question": "Get customers with more than 2 orders",
        "difficulty": "hard",
        "schema": "orders(customer_id)",
        "expected_query": "SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) > 2",
        "correct_output": [],
        "required_tables": ["orders"],
        "required_keywords": ["GROUP BY", "HAVING"]
    },
    {
        "id": 14,
        "question": "Find average product price",
        "difficulty": "hard",
        "schema": "products(price)",
        "expected_query": "SELECT AVG(price) FROM products",
        "correct_output": [],
        "required_tables": ["products"],
        "required_keywords": ["AVG"]
    },
    {
        "id": 15,
        "question": "Get latest order",
        "difficulty": "hard",
        "schema": "orders(id)",
        "expected_query": "SELECT * FROM orders ORDER BY id DESC LIMIT 1",
        "correct_output": [],
        "required_tables": ["orders"],
        "required_keywords": ["ORDER BY", "LIMIT"]
    }
]
