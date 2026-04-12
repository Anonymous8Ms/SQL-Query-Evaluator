import sqlite3

conn = sqlite3.connect(":memory:", check_same_thread=False)


def init_db():
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        city TEXT,
        email TEXT
    )"""
    )
    cursor.execute(
        """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        category TEXT
    )"""
    )
    cursor.execute(
        """
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        total REAL,
        date TEXT
    )"""
    )
    cursor.execute(
        """
    CREATE TABLE order_items (
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER
    )"""
    )

    cursor.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?)",
        [
            (1, "Anuttama", "Bengaluru", "a@email.com"),
            (2, "Rahul", "Mumbai", "r@email.com"),
            (3, "Priya", "Delhi", "p@email.com"),
        ],
    )
    cursor.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?)",
        [
            (1, "Laptop", 55000, "Electronics"),
            (2, "Mouse", 800, "Accessories"),
            (3, "Keyboard", 2200, "Accessories"),
            (4, "Monitor", 18000, "Electronics"),
        ],
    )
    cursor.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?)",
        [
            (1, 2, 6800, "2026-01-15"),
            (2, 1, 3200, "2026-01-22"),
            (3, 3, 1200, "2026-02-10"),
            (4, 1, 1800, "2026-02-14"),
        ],
    )
    cursor.executemany(
        "INSERT INTO order_items VALUES (?, ?, ?)",
        [
            (1, 1, 1),
            (1, 2, 2),
            (2, 3, 1),
            (2, 2, 1),
            (3, 2, 1),
            (4, 4, 1),
        ],
    )
    conn.commit()


init_db()


def get_db_connection():
    return conn

