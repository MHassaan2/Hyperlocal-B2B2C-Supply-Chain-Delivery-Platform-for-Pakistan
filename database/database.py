import sqlite3
import os
#DATABASE = "database/database.db"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, "database", "database.db")
def get_db_connection():
    connection= sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def create_user_table():
    connection = get_db_connection()
    connection.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_AT TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()
    print("User table created successfully!")

def create_products_table():
    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wholesaler_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (wholesaler_id) REFERENCES users(id)
        )
    """)
    connection.commit()
    connection.close()
    print("Products table created successfully!")

def create_address_table():
    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            state TEXT NOT NULL,
            city TEXT NOT NULL,
            address_line TEXT NOT NULL,
            postal_code TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    connection.commit()
    connection.close()
    print("Addresses table created successfully!")

def create_orders_table():
    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shopkeeper_id INTEGER NOT NULL,
            wholesaler_id INTEGER NOT NULL,
            address_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (shopkeeper_id) REFERENCES users(id),
            FOREIGN KEY (wholesaler_id) REFERENCES users(id),
            FOREIGN KEY (address_id) REFERENCES addresses(id)
        )
    """)
    connection.commit()
    connection.close()
    print("Orders table created successfully!")

def create_order_items_table():
    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    connection.commit()
    connection.close()
    print("Order items table created successfully!")

def create_cart_table():
    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shopkeeper_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (shopkeeper_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    connection.commit()
    connection.close()
    print("Cart table created successfully!")


if __name__ == "__main__":
    connection = get_db_connection()
    print("Database connection successful!")
    user=create_user_table()
    address=create_address_table()
    products=create_products_table()
    orders=create_orders_table()
    order_items=create_order_items_table()
    cart=create_cart_table()
    connection.close()
