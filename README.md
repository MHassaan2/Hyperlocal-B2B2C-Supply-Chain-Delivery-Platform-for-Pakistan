# Hyperlocal B2B2C Supply Chain & Delivery Platform for Pakistan
 
A Flask-based web platform designed to connect wholesalers with local shopkeepers and simplify product purchasing and order management.
 
## 📌 Overview
 
The platform provides role-based functionality for:
 
- Shopkeepers
- Wholesalers
- Administrators
It supports product management, shopping, checkout, order processing, and order tracking.
 
## ✨ Features
 
### 🔐 Authentication
 
- User registration
- Secure password hashing
- User login and logout
- Session management
- Role-based access control
### 📦 Wholesaler
 
- Wholesaler dashboard
- Add products
- View products
- Edit products
- Delete products
- Manage product stock
- View incoming orders
- Update order status
### 🛒 Shopkeeper
 
- Shopkeeper dashboard
- Browse products
- Search products
- View prices and stock
- Add products to cart
- Manage cart
- Checkout
- Place orders
- View order history
- Track order status
### 🛡️ Admin
 
- Admin dashboard
- User management
- Product monitoring
- Order monitoring
- Wholesaler management
## 🔄 System Workflow
 
```text
Registration
     ↓
    Login
     ↓
Role-Based Dashboard
     ↓
Shopkeeper → Products → Cart → Checkout → Order Tracking
     ↓
Wholesaler → Products → Incoming Orders → Status Updates
     ↓
Admin → Users → Products → Orders → Management
```
 
## 🗄️ Database
 
The project currently uses SQLite.
 
Main database tables:
 
- Users
- Products
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
├── database/
│   ├── database.py
│   └── database.db
├── static/
│   ├── css/
│   ├── images/
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
 
**6. Run Application**
 
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
## 📄 License
 
This project is developed for academic and educational purposes.