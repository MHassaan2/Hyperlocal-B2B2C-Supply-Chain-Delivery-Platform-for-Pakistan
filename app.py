from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import get_db_connection
from datetime import datetime

app = Flask(__name__)

app.config["SECRET_KEY"] = "hyperlocal-secret-key"


@app.route("/")
def home():
    return render_template("base.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        connection = get_db_connection()
        hashed_password = generate_password_hash(password)
        try:
            connection.execute("""
            INSERT INTO users (name, email, password, role, created_AT) VALUES (?, ?, ?, ?, ?)
            """, (name, 
                  email, 
                  hashed_password, 
                  role, 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            connection.commit()
            flash("User registered successfully!", "success")
        except Exception as e:
            connection.rollback()
            flash(f"Registration failed: "+ str(e), "error")
        finally:
            connection.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        connection = get_db_connection()
        user = connection.execute("""
            SELECT * FROM users WHERE email = ?
        """, (email,)).fetchone()
        connection.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "error")
    return render_template("login.html")

def is_logged_in():
    return "user_id" in session

def has_role(role):
    return is_logged_in() and session.get("user_role") == role


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    role = session["user_role"]
    if role == "Shopkeeper":
        return render_template("shopkeeper/dashboard.html")
    elif role == "Wholesaler":
        return render_template("wholesaler/dashboard.html")
    elif role == "Admin":
        return render_template("admin/dashboard.html")
    else:
        flash("Invalid user role.", "error")
        return redirect(url_for("login"))

@app.route("/wholesaler/add-product", methods=["GET", "POST"])
def add_product():
    if not has_role("Wholesaler"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        stock = request.form["stock"]
        category = request.form["category"]
        connection = get_db_connection()
        try:
            connection.execute("""
                INSERT INTO products
                (wholesaler_id, name, description, price, stock, category, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session["user_id"],
                name,
                description,
                price,
                stock,
                category,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            connection.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for("add_product"))
        except Exception as e:
            connection.rollback()
            flash("Failed to add product: " + str(e), "error")
        finally:
            connection.close()
    return render_template("wholesaler/add_product.html")

@app.route("/wholesaler/products")
def wholesaler_products():
    if not has_role("Wholesaler"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    connection = get_db_connection()
    products = connection.execute("""
        SELECT *
        FROM products
        WHERE wholesaler_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()
    if not products:
        flash("No products found.", "info")
    connection.close()
    return render_template(
        "wholesaler/products.html",
        products=products
    )

@app.route("/wholesaler/edit-product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if not has_role("Wholesaler"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    connection = get_db_connection()
    product = connection.execute("""
        SELECT *
        FROM products
        WHERE id = ? AND wholesaler_id = ?
    """, (product_id, session["user_id"])).fetchone()
    if not product:
        connection.close()
        flash("Product not found.", "error")
        return redirect(url_for("wholesaler_products"))
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        stock = request.form["stock"]
        category = request.form["category"]
        try:
            connection.execute("""
                UPDATE products
                SET name = ?,
                    description = ?,
                    price = ?,
                    stock = ?,
                    category = ?
                WHERE id = ? AND wholesaler_id = ?
            """, (
                name,
                description,
                price,
                stock,
                category,
                product_id,
                session["user_id"]
            ))
            connection.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("wholesaler_products"))
        except Exception as e:
            connection.rollback()
            flash("Failed to update product: " + str(e), "error")
        finally:
            connection.close()
    else:
        connection.close()
    return render_template(
        "wholesaler/edit_product.html",
        product=product
    )

@app.route("/wholesaler/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if not has_role("Wholesaler"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    connection = get_db_connection()
    try:
        product = connection.execute("""
            SELECT id
            FROM products
            WHERE id = ? AND wholesaler_id = ?
        """, (product_id, session["user_id"])).fetchone()
        if not product:
            flash("Product not found.", "error")
            return redirect(url_for("wholesaler_products"))
        connection.execute("""
            DELETE FROM products
            WHERE id = ? AND wholesaler_id = ?
        """, (product_id, session["user_id"]))
        connection.commit()
        flash("Product deleted successfully!", "success")
    except Exception as e:
        connection.rollback()
        flash("Failed to delete product: " + str(e), "error")
    finally:
        connection.close()
    return redirect(url_for("wholesaler_products"))

@app.route("/wholesaler/orders")
def wholesaler_orders():
    if not has_role("Wholesaler"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    connection = get_db_connection()
    orders = connection.execute("""
        SELECT *
        FROM orders
        WHERE wholesaler_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()
    if not orders:
        flash("No orders found.", "info")
    connection.close()
    return render_template(
        "wholesaler/orders.html",
        orders=orders
    )

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


        


if __name__ == "__main__":
    app.run(debug=True)