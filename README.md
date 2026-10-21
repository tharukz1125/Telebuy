# TeleBuy.lk — Smart TVs & Accessories Online Marketplace

Production-ready e-commerce platform for **TeleBuy.lk**, featuring native **MySQL relational database persistence**, official **PayHere Online Payment Gateway** integration (sandbox & live), Cash on Delivery (COD) processing, and real-time **7-stage delivery tracking**.

---

## 1. System Architecture

- **Frontend**: Plain HTML5, CSS3 (with responsive layout, light/dark mode), and modular Vanilla JavaScript (`store.js`, `auth.js`).
- **Backend**: Native Python backend server (`server.py`) powered by `ThreadingHTTPServer` and `pymysql`.
- **Database**: **MySQL / MariaDB (`telebuy_db`)** using the InnoDB storage engine and `utf8mb4_unicode_ci` character encoding.
- **Payment Gateway**: **PayHere** with server-side MD5 HMAC cryptographic signature generation, IPN webhook signature verification, and idempotency protection.

---

## 2. MySQL Database Schema (`telebuy_db`)

The database consists of 9 fully normalized relational tables:

| Table | Description | Key Relationships |
|---|---|---|
| `categories` | Product categories (QLED, OLED, 8K, Smart, LED, Accessories) | Referenced by `products.category_id` |
| `products` | Authoritative catalog with live price, stock, and specs | Referenced by `order_items` & `cart_items` |
| `users` | Customer & Admin accounts with salted SHA-256 hashes | Referenced by `orders`, `shipping_addresses` |
| `shipping_addresses` | Customer delivery addresses with defaults | Foreign key to `users.id` (ON DELETE CASCADE) |
| `cart_items` | Persistent user shopping carts | Foreign keys to `users.id` & `products.product_id` |
| `orders` | Master orders with tracking, payment status & totals | Foreign key to `users.id` (ON DELETE SET NULL) |
| `order_items` | Purchased items snapshot with unit prices & line totals | Foreign key to `orders.id` (ON DELETE CASCADE) |
| `payments` | Audit log of all PayHere transactions & gateway statuses | Foreign key to `orders.id` (ON DELETE CASCADE) |
| `order_status_history` | Audit timeline for the 7 official delivery stages | Foreign key to `orders.id` (ON DELETE CASCADE) |

---

## 3. Database Setup & Initialization

### Option A: Automatic Initialization & Migration (Recommended)
Run the automated initialization script:
```powershell
python database/init_and_migrate.py
```
This script:
1. Connects to MySQL and creates `telebuy_db` if it does not exist.
2. Applies `database/schema.sql` to construct all 9 tables, indexes, and foreign keys.
3. Applies `database/seed.sql` to populate all 34 TV products and default accounts without creating duplicates.
4. Safely migrates any historical orders from previous sessions.

### Option B: Using MySQL Workbench
1. Open **MySQL Workbench** and connect to your local MySQL instance (`localhost:3306`).
2. Open `database/schema.sql` (File → Open SQL Script...) and click the **Execute** lightning bolt icon.
3. Open `database/seed.sql` and execute it to populate products and initial users.

### Option C: Using MySQL Command Line
```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS telebuy_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p telebuy_db < database/schema.sql
mysql -u root -p telebuy_db < database/seed.sql
```

---

## 4. Environment Variables Configuration

Create or update `.env` in the project root:

```ini
# Server Configuration
PORT=3000
BASE_URL=http://localhost:3000

# MySQL Database Configuration
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=telebuy_db
DB_USER=root
DB_PASSWORD=

# PayHere Payment Gateway Credentials
PAYHERE_MODE=sandbox
MERCHANT_ID=1238371
MERCHANT_SECRET=NDE2Njk4MTMzNzE3ODQzNjI3NjMzNzQ0NjI1MTAyMzgwNTM1MzgwNA==

# Admin Management API Key
ADMIN_SECRET_KEY=telebuy_admin_secret_2026
```

---

## 5. Running the Application

1. Make sure MySQL is running (e.g. via XAMPP Control Panel, MySQL Service, or Docker).
2. Start the backend server:
   ```powershell
   python server.py
   ```
3. Open your browser and navigate to:
   - **Storefront**: [http://localhost:3000](http://localhost:3000)
   - **Customer Orders & Tracking**: [http://localhost:3000/orders.html](http://localhost:3000/orders.html)
   - **Admin Portal**: [http://localhost:3000/admin-orders.html](http://localhost:3000/admin-orders.html)

*(Note: If you use VS Code Live Server on port 5500, the frontend automatically routes all API requests to `http://localhost:3000` via the dynamic `getApiBaseUrl()` helper).*

---

## 6. Pre-Seeded Accounts

- **Administrator Account**:
  - Email: `admin@telebuy.lk`
  - Password: `AdminPass123!`
  - Role: `admin`
- **Customer Demo Account**:
  - Email: `student@telebuy.lk`
  - Password: `Password123!`
  - Role: `customer`

---

## 7. Verifying Real Records in MySQL

You can inspect the database at any time using MySQL Workbench, phpMyAdmin (`http://localhost/phpmyadmin`), or the command line:

```sql
USE telebuy_db;

-- 1. View all orders with payment & delivery status
SELECT order_id, customer_name, total_amount, payment_method, payment_status, delivery_status, created_at 
FROM orders ORDER BY id DESC;

-- 2. Inspect order items for a specific order
SELECT o.order_id, i.title, i.qty, i.unit_price, i.line_total 
FROM orders o 
JOIN order_items i ON o.id = i.order_id 
ORDER BY o.id DESC;

-- 3. View verified PayHere payment records
SELECT * FROM payments ORDER BY id DESC;

-- 4. View delivery tracking audit history
SELECT o.order_id, h.stage, h.description, h.updated_by, h.timestamp 
FROM orders o 
JOIN order_status_history h ON o.id = h.order_id 
ORDER BY h.id DESC;
```

---

## 8. Running the Automated Test Suite

A complete test suite is included to verify all database operations, PayHere hashing, IPN webhooks, idempotency, and admin controls:

```powershell
python tests/test_mysql_suite.py
```

Expected output:
```
=================================================================
  TELEBUY.LK — COMPLETE MYSQL INTEGRATION TEST SUITE
=================================================================
[1/1] PASS: Database Connection verified. DB='mysql', Database='telebuy_db'.
[2/2] PASS: Product and Category retrieval from MySQL verified.
[3/3] PASS: User Registration persisted directly to MySQL `users` table.
[4/4] PASS: User Login authenticated via MySQL password hash.
[5/5] PASS: COD Order and Order Items saved to MySQL (`orders` & `order_items`).
[6/6] PASS: PayHere order created in MySQL with MD5 signature.
[7/7] PASS: PayHere IPN verified. Order updated to PAID and payment record saved in MySQL `payments`.
[8/8] PASS: Duplicate payment notification handled idempotently without re-processing.
[9/9] PASS: Fraudulent payment webhook rejected with HTTP 400.
[10/10] PASS: Order tracking retrieved from MySQL with 7-stage delivery stepper.
[11/11] PASS: Admin authorization enforced & delivery status advanced to 'Shipped' in MySQL.
[12/12] PASS: MySQL InnoDB Foreign-Key constraints verified (8 relational keys).
=================================================================
  ALL 12/12 MYSQL INTEGRATION TESTS PASSED WITH 100% SUCCESS!
=================================================================
```