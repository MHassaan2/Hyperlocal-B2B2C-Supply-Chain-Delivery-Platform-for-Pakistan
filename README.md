# Hyperlocal B2B2C Supply Chain & Delivery Platform for Pakistan
 
A Flask-based web platform designed to connect wholesalers with local shopkeepers and simplify product purchasing and order management.
 
## 📌 Overview
 
The platform provides role-based functionality for:
 
- Shopkeepers
- Wholesalers
- Administrators
It supports product management (with images), shopping, checkout, order processing with a full status lifecycle, order tracking, and admin oversight of users, products, and orders.
 
## ✨ Features
 
### 🔐 Authentication
 
- User registration with role selection (Shopkeeper / Wholesaler)
- Password strength validation (min 8 characters, 1 uppercase, 1 number, 1 special character)
- Secure password hashing
- Phone number required for all users
- Business name and city required for wholesalers
- User login and logout
- Session management
- Role-based access control
- Disabled wholesaler accounts are blocked from logging in
### 📦 Wholesaler
 
- Wholesaler dashboard
- Add products with an image upload
- View, edit, and delete products
- Manage product stock
- View incoming orders with customer name, phone, and delivery address
- Update order status (Pending → Confirmed → Dispatched → Delivered, or Cancelled)
- Automatic stock restoration when an order is cancelled
### 🛒 Shopkeeper
 
- Shopkeeper dashboard
- Browse products with images, wholesaler business name, contact number, and city
- Search products by name, category, or description
- View prices and stock
- Add products to cart, update quantities, remove items
- Checkout with delivery address entry
- Validation against checking out with products from multiple wholesalers
- Automatic order ID generation (`ORD-<shopkeeper_id>-<order_id>`)
- View order history with wholesaler contact details
- Public order tracking page with a visual progress tracker
### 🛡️ Admin
 
- Admin dashboard
- Manage Users — view and delete Shopkeeper/Wholesaler accounts, with cascading removal of their related orders, cart items, addresses, and (for wholesalers) products
- Manage Wholesalers — view all wholesalers and enable/disable their accounts
- Manage Products — view all products platform-wide and remove any listing
- Manage Orders — view all orders across every shopkeeper and wholesaler
## 🔄 System Workflow
 
```text
Registration
     ↓
    Login
     ↓
Role-Based Dashboard
     ↓
Shopkeeper → Browse Products → Cart → Checkout → Order Tracking
     ↓
Wholesaler → Manage Products → Incoming Orders → Status Updates
     ↓
Admin → Users → Wholesalers → Products → Orders → Platform Oversight
```
 
## 📦 Order Status Lifecycle
 
```text
Pending → Confirmed → Dispatched → Delivered
   ↓            ↓
Cancelled   Cancelled
```
 
Cancelling a Pending or Confirmed order automatically restores the reserved product stock.
 
## 🗄️ Database
 
The project currently uses SQLite.
 
Main database tables:
 
- Users (includes phone, business_name, city_name, is_active)
- Products (includes image)
- Addresses
- Orders
- Order Items
- Cart
## 🛠️ Technology Stack
 
- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Jinja2
- Git
- GitHub
## 📁 Project Structure
 
```text
project/
├── app.py
├── create_admin.py
├── database/
│   ├── database.py
│   └── database.db
├── static/
│   ├── css/
│   ├── images/
│   │   └── products/
│   └── js/
└── templates/
    ├── admin/
    ├── shopkeeper/
    ├── wholesaler/
    ├── base.html
    ├── login.html
    ├── register.html
    └── 404.html
```
 
## 🚀 Installation
 
**1. Clone Repository**
 
```bash
git clone https://github.com/MHassaan2/Hyperlocal-B2B2C-Supply-Chain-Delivery-Platform-for-Pakistan.git
```
 
**2. Open Project**
 
```bash
cd Hyperlocal-B2B2C-Supply-Chain-Delivery-Platform-for-Pakistan
```
 
**3. Create Virtual Environment**
 
```bash
python -m venv .venv
```
 
**4. Activate Environment**
 
Windows PowerShell:
 
```bash
.\.venv\Scripts\Activate.ps1
```
 
**5. Install Dependencies**
 
```bash
pip install flask werkzeug
```
 
**6. Create the First Admin Account**
 
Since Admin accounts cannot be created through public registration, run the one-time seed script:
 
```bash
python create_admin.py
```
 
**7. Run Application**
 
```bash
python app.py
```
 
Open:
 
```text
http://127.0.0.1:5000
```
 
## 📸 Screenshots
 
Screenshots of the following pages can be added here:
 
- Home Page
- Login
- Registration
- Shopkeeper Dashboard
- Product Browsing
- Shopping Cart
- Checkout
- Order Tracking
- Wholesaler Dashboard
- Product Management
- Admin Dashboard
- Admin: Manage Users / Wholesalers / Products / Orders
## 🎓 Academic Information
 
- **Course:** Python Programming
- **Instructor:** Abdullah Nasir
- **Organization:** iSeeWaves
- **Purpose:** Academic Project
**Team Members**
 
- Muhammad Hassaan
- Syeda Gulnoor Fatima
## 🔮 Future Enhancements
 
- Online payment integration
- Real-time delivery tracking
- Mobile application
- Cloud database deployment
- Notifications
- Advanced analytics
- Enhanced security
- Immediate session invalidation on account disable
## 📄 License
 
This project is developed for academic and educational purposes.
