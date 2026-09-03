# create_admin.py
from werkzeug.security import generate_password_hash
from database.database import get_db_connection
from datetime import datetime
    
connection = get_db_connection()
hashed_password = generate_password_hash("YourStrongPass1!")  # meets your password rules
phone_number = "1234567890"  # Replace with a valid phone number
connection.execute("""
    INSERT INTO users (name, email, password, role, phone, business_name, city_name, created_AT)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "Admin",
    "admin@hyperlocal.com",
    hashed_password,
    "Admin",
    phone_number,
    "Hyperlocal Admin",
    "Admin City",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
))
connection.commit()
connection.close()
print("Admin account created.")