import sqlite3


DATABASE = "ecommerce.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def create_database():

    connection = get_connection()
    cursor = connection.cursor()

    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            product_name TEXT NOT NULL,
            order_date TEXT NOT NULL,
            delivery_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    # Chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sample orders
    orders = [
        (
            "ORD1001",
            "Abisha",
            "Smart Watch",
            "2026-08-20",
            "2026-08-29",
            "Shipped"
        ),
        (
            "ORD1002",
            "Abisha",
            "Wireless Headphones",
            "2026-08-21",
            "2026-08-28",
            "Delivered"
        ),
        (
            "ORD1003",
            "Abisha",
            "Smartphone",
            "2026-08-22",
            "2026-08-30",
            "Processing"
        )
    ]

    for order in orders:

        cursor.execute("""
            INSERT OR IGNORE INTO orders
            (
                order_id,
                customer_name,
                product_name,
                order_date,
                delivery_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, order)

    # Sample products
    products = [
        ("Smart Watch", 1999, 25),
        ("Wireless Headphones", 1499, 30),
        ("Smartphone", 15999, 15),
        ("Laptop", 54999, 10),
        ("Bluetooth Speaker", 2499, 20)
    ]

    for product in products:

        cursor.execute("""
            INSERT OR IGNORE INTO products
            (product_name, price, stock)
            VALUES (?, ?, ?)
        """, product)

    connection.commit()
    connection.close()

    print("Database created successfully!")


def get_order(order_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            customer_name,
            product_name,
            order_date,
            delivery_date,
            status
        FROM orders
        WHERE UPPER(order_id) = ?
    """, (order_id.upper(),))

    order = cursor.fetchone()

    connection.close()

    return order


def get_product(product_name):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_name, price, stock
        FROM products
        WHERE LOWER(product_name) LIKE ?
        LIMIT 1
    """, ("%" + product_name.lower() + "%",))

    product = cursor.fetchone()

    connection.close()

    return product


def save_chat(user_message, bot_response, detected_intent):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO chat_history
        (
            user_message,
            bot_response,
            detected_intent
        )
        VALUES (?, ?, ?)
    """, (
        user_message,
        bot_response,
        detected_intent
    ))

    connection.commit()
    connection.close()


def get_chat_history():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            user_message,
            bot_response,
            timestamp
        FROM chat_history
        ORDER BY id ASC
    """)

    history = cursor.fetchall()

    connection.close()

    return history


def clear_chat_history():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM chat_history
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()