import re
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database.database import get_db_connection
from datetime import datetime



app = Flask(__name__)

app.config["SECRET_KEY"] = "hyperlocal-secret-key"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
UPLOAD_FOLDER = os.path.join("static", "images", "products")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        phone = request.form["phone"]
        business_name = request.form.get("business_name") if role == "Wholesaler" else None
        city_name = request.form.get("city_name") if role == "Wholesaler" else None

        # Password validation
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", password):
            errors.append("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=~`\[\]\\/;']", password):
            errors.append("Password must contain at least one special character.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("register.html")

        connection = get_db_connection()
        hashed_password = generate_password_hash(password)
        try:
            connection.execute("""
            INSERT INTO users (name, email, password, role, phone, business_name, city_name, created_AT) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, 
                  email, 
                  hashed_password, 
                  role,
                  phone,
                  business_name,
                  city_name,
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

@app.route("/")
def home():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return render_template("base.html")


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
        # Handle image upload
        image_filename = None
        file = request.files.get("image")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Invalid image type. Use PNG, JPG, JPEG, or WEBP.", "error")
                return render_template("wholesaler/add_product.html")
            ext = file.filename.rsplit(".", 1)[1].lower()
            image_filename = f"{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, image_filename))
        connection = get_db_connection()
        try:
            connection.execute("""
                INSERT INTO products
                (wholesaler_id, name, description, price, stock, category, image, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session["user_id"],
                name,
                description,
                price,
                stock,
                category,
                image_filename,
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
        image_filename = product["image"]  # keep existing by default
        file = request.files.get("image")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Invalid image type. Use PNG, JPG, JPEG, or WEBP.", "error")
                connection.close()
                return render_template("wholesaler/edit_product.html", product=product)
            ext = file.filename.rsplit(".", 1)[1].lower()
            image_filename = f"{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, image_filename))
            # Remove old image file if one existed
            if product["image"]:
                old_path = os.path.join(UPLOAD_FOLDER, product["image"])
                if os.path.exists(old_path):
                    os.remove(old_path)
        try:
            connection.execute("""
                UPDATE products
                SET name = ?,
                    description = ?,
                    price = ?,
                    image = ?,
                    stock = ?,
                    category = ?
                WHERE id = ? AND wholesaler_id = ?
            """, (
                name,
                description,
                price,
                image_filename,
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

@app.route("/wholesaler/incoming_orders")
def wholesaler_orders():
    if not has_role("Wholesaler"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    connection = get_db_connection()
    orders = connection.execute("""
       SELECT
            orders.*,
            users.name AS customer_name,
            users.phone AS customer_phone,
            addresses.address_line,
            addresses.city,
            addresses.state,
            addresses.postal_code
        FROM orders
        JOIN users ON orders.shopkeeper_id = users.id
        JOIN addresses ON orders.address_id = addresses.id
        WHERE orders.wholesaler_id = ?
        ORDER BY orders.id DESC
    """, (session["user_id"],)).fetchall()
    if not orders:
        flash("No orders found.", "info")
    connection.close()
    return render_template(
        "wholesaler/incoming_orders.html",
        orders=orders
    )

@app.route("/wholesaler/update_order/<int:order_id>/<status>")
def update_order(order_id, status):
    if not has_role("Wholesaler"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))

    allowed_statuses = ["Pending","Confirmed", "Dispatched", "Delivered", "Cancelled"]
    if status not in allowed_statuses:
        flash("Invalid status.", "error")
        return redirect(url_for("wholesaler_orders"))

    connection = get_db_connection()
    try:
        order = connection.execute("""
            SELECT id, status FROM orders
            WHERE id = ? AND wholesaler_id = ?
        """, (order_id, session["user_id"])).fetchone()
        if not order:
            flash("Order not found.", "error")
            return redirect(url_for("wholesaler_orders"))

        # Restore stock if cancelling an order that hadn't already been cancelled
        if status == "Cancelled" and order["status"] != "Cancelled":
            items = connection.execute("""
                SELECT product_id, quantity FROM order_items
                WHERE order_id = ?
            """, (order_id,)).fetchall()
            for item in items:
                connection.execute("""
                    UPDATE products SET stock = stock + ?
                    WHERE id = ?
                """, (item["quantity"], item["product_id"]))

        connection.execute("""
            UPDATE orders SET status = ?
            WHERE id = ? AND wholesaler_id = ?
        """, (status, order_id, session["user_id"]))
        connection.commit()
        flash(f"Order #{order_id} marked as {status}.", "success")
    except Exception as e:
        connection.rollback()
        flash("Failed to update order: " + str(e), "error")
    finally:
        connection.close()
    return redirect(url_for("wholesaler_orders"))

@app.route("/shopkeeper/orders")
def shopkeeper_orders():
    if not has_role("Shopkeeper"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    connection = get_db_connection()
    orders = connection.execute("""
        SELECT orders.*,
               COALESCE(users.business_name, users.name) AS wholesaler_name,
               users.phone AS wholesaler_phone
        FROM orders
        JOIN users ON orders.wholesaler_id = users.id
        WHERE orders.shopkeeper_id = ?
        ORDER BY orders.id DESC
    """, (session["user_id"],)).fetchall()
    connection.close()
    return render_template(
        "shopkeeper/orders.html",
        orders=orders
    )

@app.route("/shopkeeper/cart")
def shopkeeper_cart():
    if not has_role("Shopkeeper"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    connection = get_db_connection()
    try:
        cart_items = connection.execute("""
            SELECT
                cart.id,
                cart.product_id,
                cart.quantity,
                products.name,
                products.description,
                products.price,
                products.stock
            FROM cart
            JOIN products
                ON cart.product_id = products.id
            WHERE cart.shopkeeper_id = ?
            ORDER BY cart.id DESC
        """, (
            session["user_id"],
        )).fetchall()
        total_amount = sum(
            item["price"] * item["quantity"]
            for item in cart_items
        )
        return render_template(
            "shopkeeper/cart.html",
            cart_items=cart_items,
            total_amount=total_amount
        )
    finally:
        connection.close()

@app.route("/shopkeeper/checkout", methods=["GET", "POST"])
def checkout():
    if not has_role("Shopkeeper"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    connection = get_db_connection()
    try:
        # Cart items
        cart_items = connection.execute("""
            SELECT
                cart.id,
                cart.product_id,
                cart.quantity,
                products.name AS product_name,
                products.price,
                products.stock,
                products.wholesaler_id
            FROM cart
            JOIN products
                ON cart.product_id = products.id
            WHERE cart.shopkeeper_id = ?
        """, (session["user_id"],)).fetchall()
        # Empty cart
        if not cart_items:
            flash("Your cart is empty.", "error")
            return redirect(url_for("shopkeeper_cart"))
        # Make sure all products belong to the same wholesaler
        wholesaler_ids = set(
            item["wholesaler_id"] for item in cart_items
        )
        if len(wholesaler_ids) > 1:
            flash(
                "Products from different wholesalers cannot be placed in one order.",
                "error"
            )
            return redirect(url_for("shopkeeper_cart"))
        wholesaler_id = cart_items[0]["wholesaler_id"]
        # Calculate total
        total_amount = sum(
            item["price"] * item["quantity"]
            for item in cart_items
        )
        # Place order
        if request.method == "POST":
            address_line = request.form["address_line"]
            city = request.form["city"]
            state = request.form["state"]
            postal_code = request.form.get("postal_code")
            created_at = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            # Create address
            cursor = connection.execute("""
                INSERT INTO addresses
                (user_id, state, city, address_line, postal_code, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session["user_id"],
                state,
                city,
                address_line,
                postal_code,
                created_at
            ))
            address_id = cursor.lastrowid
            # Create order
            cursor = connection.execute("""
                INSERT INTO orders
                (shopkeeper_id, wholesaler_id, address_id,
                 total_amount, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session["user_id"],
                wholesaler_id,
                address_id,
                total_amount,
                "Pending",
                created_at
            ))
            order_id = cursor.lastrowid
            # Create order items
            for item in cart_items:
                connection.execute("""
                    INSERT INTO order_items
                    (order_id, product_id, quantity, price, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    order_id,
                    item["product_id"],
                    item["quantity"],
                    item["price"],
                    created_at
                ))
                # Reduce product stock
                connection.execute("""
                    UPDATE products
                    SET stock = stock - ?
                    WHERE id = ?
                """, (
                    item["quantity"],
                    item["product_id"]
                ))
            # Clear cart
            connection.execute("""
                DELETE FROM cart
                WHERE shopkeeper_id = ?
            """, (session["user_id"],))
            connection.commit()
            flash(
                f"Order #ORD-{session['user_id']}-{order_id} placed successfully!",
                "success"
            )
            return redirect(url_for("shopkeeper_orders"))
        return render_template(
            "shopkeeper/checkout.html",
            cart_items=cart_items,
            total_amount=total_amount
        )
    except Exception as e:
        connection.rollback()
        flash(
            "Checkout failed: " + str(e),
            "error"
        )
        return redirect(url_for("shopkeeper_cart"))
    finally:
        connection.close()

@app.route("/shopkeeper/products")
def shopkeeper_products():
    if not has_role("Shopkeeper"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    if search:
        like_term = f"%{search}%"
        products = connection.execute("""
            SELECT p.*,
                   COALESCE(u.business_name, u.name) AS wholesaler_name,
                   u.phone AS wholesaler_phone,
                   u.city_name AS wholesaler_city
            FROM products p
            JOIN users u ON p.wholesaler_id = u.id
            WHERE p.name LIKE ?
               OR p.category LIKE ?
               OR p.description LIKE ?
            ORDER BY p.id DESC
        """, (like_term, like_term, like_term)).fetchall()
    else:
        products = connection.execute("""
            SELECT p.*,
                   COALESCE(u.business_name, u.name) AS wholesaler_name,
                   u.phone AS wholesaler_phone,
                   u.city_name AS wholesaler_city
            FROM products p
            JOIN users u ON p.wholesaler_id = u.id
            ORDER BY p.id DESC
        """).fetchall()
    connection.close()

    return render_template(
        "shopkeeper/products.html",
        products=products,
        search=search
    )

@app.route("/shopkeeper/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if not has_role("Shopkeeper"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    connection = get_db_connection()
    try:
        # Check product exists
        product = connection.execute("""
            SELECT *
            FROM products
            WHERE id = ?
        """, (product_id,)).fetchone()
        if not product:
            flash("Product not found.", "error")
            return redirect(url_for("shopkeeper_products"))
        # Check stock
        if product["stock"] <= 0:
            flash("Product is out of stock.", "error")
            return redirect(url_for("shopkeeper_products"))
        # Check if product already exists in cart
        existing_item = connection.execute("""
            SELECT *
            FROM cart
            WHERE shopkeeper_id = ?
            AND product_id = ?
        """, (
            session["user_id"],
            product_id
        )).fetchone()
        if existing_item:
            new_quantity = existing_item["quantity"] + 1
            if new_quantity > product["stock"]:
                flash("Not enough stock available.", "error")
                return redirect(url_for("shopkeeper_products"))
            connection.execute("""
                UPDATE cart
                SET quantity = ?
                WHERE id = ?
            """, (
                new_quantity,
                existing_item["id"]
            ))
        else:
            connection.execute("""
                INSERT INTO cart
                (shopkeeper_id, product_id, quantity, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                session["user_id"],
                product_id,
                1,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        connection.commit()
        flash("Product added to cart.", "success")
    except Exception as e:
        connection.rollback()
        flash(
            "Failed to add product to cart: " + str(e),
            "error"
        )
    finally:
        connection.close()
    return redirect(url_for("shopkeeper_products"))

@app.route("/shopkeeper/cart/update/<int:cart_id>", methods=["POST"])
def update_cart(cart_id):
    if not has_role("Shopkeeper"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    quantity = int(request.form["quantity"])
    if quantity < 1:
        flash("Quantity must be at least 1.", "error")
        return redirect(url_for("shopkeeper_cart"))
    connection = get_db_connection()
    try:
        item = connection.execute("""
            SELECT
                cart.id,
                cart.product_id,
                products.stock
            FROM cart
            JOIN products
                ON cart.product_id = products.id
            WHERE cart.id = ?
            AND cart.shopkeeper_id = ?
        """, (
            cart_id,
            session["user_id"]
        )).fetchone()
        if not item:
            flash("Cart item not found.", "error")
            return redirect(url_for("shopkeeper_cart"))
        if quantity > item["stock"]:
            flash("Not enough stock available.", "error")
            return redirect(url_for("shopkeeper_cart"))
        connection.execute("""
            UPDATE cart
            SET quantity = ?
            WHERE id = ?
            AND shopkeeper_id = ?
        """, (
            quantity,
            cart_id,
            session["user_id"]
        ))
        connection.commit()
        flash("Cart updated successfully.", "success")
    except Exception as e:
        connection.rollback()
        flash(
            "Failed to update cart: " + str(e),
            "error"
        )
    finally:
        connection.close()
    return redirect(url_for("shopkeeper_cart"))

@app.route("/shopkeeper/cart/remove/<int:cart_id>", methods=["POST"])
def remove_from_cart(cart_id):
    if not has_role("Shopkeeper"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    connection = get_db_connection()
    try:
        item = connection.execute("""
            SELECT id
            FROM cart
            WHERE id = ?
            AND shopkeeper_id = ?
        """, (
            cart_id,
            session["user_id"]
        )).fetchone()
        if not item:
            flash("Cart item not found.", "error")
            return redirect(url_for("shopkeeper_cart"))
        connection.execute("""
            DELETE FROM cart
            WHERE id = ?
            AND shopkeeper_id = ?
        """, (
            cart_id,
            session["user_id"]
        ))
        connection.commit()
        flash("Product removed from cart.", "success")
    except Exception as e:
        connection.rollback()
        flash(
            "Failed to remove product: " + str(e),
            "error"
        )
    finally:
        connection.close()
    return redirect(url_for("shopkeeper_cart"))

@app.route("/track-order")
def track_order():
    order = None
    address = None
    raw_input = request.args.get("order_id")
    if raw_input:
        match = re.match(r"^ORD-(\d+)-(\d+)$", raw_input, re.IGNORECASE)
        if match:
            shopkeeper_id, order_id = match.groups()
            connection = get_db_connection()
            try:
                order = connection.execute("""
                    SELECT * FROM orders
                    WHERE id = ? AND shopkeeper_id = ?
                """, (order_id, shopkeeper_id)).fetchone()

                if order:
                    address = connection.execute("""
                        SELECT * FROM addresses WHERE id = ?
                    """, (order["address_id"],)).fetchone()
            finally:
                connection.close()

    return render_template(
        "shopkeeper/order-tracking.html",
        order=order,
        address=address
    )

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


        


if __name__ == "__main__":
    app.run(debug=True)