"""
TeleBuy.lk — MySQL Database Initialization and SQLite Migration Script
Safely applies schema.sql, seed.sql, and migrates existing order history from SQLite.
"""

import os
import sys
import json
import sqlite3
import pymysql

# Load .env
ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(ENV_FILE):
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_NAME = os.environ.get('DB_NAME', 'telebuy_db')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

print(f"Connecting to MySQL server at {DB_HOST}:{DB_PORT} as user '{DB_USER}'...")

try:
    # 1. Connect without database first to ensure telebuy_db exists
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset='utf8mb4'
    )
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.commit()
    conn.close()
    print(f"Verified MySQL database `{DB_NAME}` exists.")

    # 2. Connect directly to telebuy_db
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    # 3. Apply schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute individual statements
        with conn.cursor() as cur:
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for stmt in statements:
                if stmt:
                    cur.execute(stmt)
        conn.commit()
        print("Successfully applied database/schema.sql.")

    # 4. Apply seed.sql
    seed_path = os.path.join(os.path.dirname(__file__), 'seed.sql')
    if os.path.exists(seed_path):
        with open(seed_path, 'r', encoding='utf-8') as f:
            seed_sql = f.read()
        
        with conn.cursor() as cur:
            statements = [s.strip() for s in seed_sql.split(';') if s.strip()]
            for stmt in statements:
                if stmt:
                    cur.execute(stmt)
        conn.commit()
        print("Successfully applied database/seed.sql.")

    # 5. Migrate existing SQLite orders if telebuy.db exists
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'telebuy.db')
    if os.path.exists(sqlite_path):
        print(f"Found SQLite database at {sqlite_path}. Checking for existing orders to migrate...")
        sq_conn = sqlite3.connect(sqlite_path)
        sq_conn.row_factory = sqlite3.Row
        sq_cur = sq_conn.cursor()

        try:
            sq_cur.execute("SELECT * FROM orders")
            orders = [dict(r) for r in sq_cur.fetchall()]
            print(f"Found {len(orders)} orders in SQLite.")

            with conn.cursor() as cur:
                for ord_row in orders:
                    # Check if order already in MySQL
                    cur.execute("SELECT id FROM orders WHERE order_id = %s", (ord_row['order_id'],))
                    existing = cur.fetchone()

                    if not existing:
                        insert_order_sql = """
                            INSERT INTO orders (
                                order_id, customer_name, customer_email, customer_phone,
                                shipping_address, subtotal, delivery_fee, total_amount, currency,
                                payment_method, payment_status, order_status, delivery_status,
                                payhere_payment_id, tracking_number, courier_name,
                                estimated_delivery, delivery_notes, created_at, updated_at
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                        """
                        cur.execute(insert_order_sql, (
                            ord_row['order_id'],
                            ord_row['customer_name'],
                            ord_row['customer_email'],
                            ord_row['customer_phone'],
                            ord_row['shipping_address'],
                            ord_row['subtotal'],
                            ord_row.get('delivery_fee', 0.0),
                            ord_row['total_amount'],
                            ord_row.get('currency', 'LKR'),
                            ord_row['payment_method'],
                            ord_row['payment_status'],
                            ord_row.get('order_status', 'Order Placed'),
                            ord_row.get('delivery_status', 'Order Placed'),
                            ord_row.get('payhere_payment_id'),
                            ord_row.get('tracking_number'),
                            ord_row.get('courier_name'),
                            ord_row.get('estimated_delivery'),
                            ord_row.get('delivery_notes'),
                            ord_row.get('created_at'),
                            ord_row.get('updated_at')
                        ))
                        mysql_order_pk = cur.lastrowid

                        # Migrate order_items
                        sq_cur.execute("SELECT * FROM order_items WHERE order_id = ?", (ord_row['order_id'],))
                        sq_items = [dict(r) for r in sq_cur.fetchall()]
                        for it in sq_items:
                            cur.execute("""
                                INSERT INTO order_items (
                                    order_id, product_id, title, brand, image, qty, unit_price, line_total
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                mysql_order_pk,
                                it.get('product_id', 'unknown'),
                                it.get('title', 'Smart TV'),
                                it.get('brand', 'TeleBuy'),
                                it.get('image', ''),
                                it.get('qty', 1),
                                it.get('unit_price', 0.0),
                                it.get('line_total', 0.0)
                            ))

                        # Migrate delivery history into order_status_history
                        sq_cur.execute("SELECT * FROM order_delivery_history WHERE order_id = ? ORDER BY id ASC", (ord_row['order_id'],))
                        sq_hist = [dict(r) for r in sq_cur.fetchall()]
                        for h in sq_hist:
                            cur.execute("""
                                INSERT INTO order_status_history (
                                    order_id, stage, description, updated_by, timestamp
                                ) VALUES (%s, %s, %s, %s, %s)
                            """, (
                                mysql_order_pk,
                                h.get('stage', 'Order Placed'),
                                h.get('description', 'Status update'),
                                h.get('updated_by', 'System'),
                                h.get('timestamp')
                            ))

                        print(f"Migrated order {ord_row['order_id']} to MySQL.")
            
            conn.commit()
            print("Completed SQLite order history migration to MySQL.")
        except Exception as mig_err:
            print(f"Note during SQLite migration: {mig_err}")
        finally:
            sq_conn.close()

    # 6. Verify table counts in MySQL
    with conn.cursor() as cur:
        for tbl in ['categories', 'products', 'users', 'shipping_addresses', 'cart_items', 'orders', 'order_items', 'payments', 'order_status_history']:
            cur.execute(f"SELECT COUNT(*) AS cnt FROM `{tbl}`")
            count = cur.fetchone()['cnt']
            print(f"Table `{tbl}`: {count} records in MySQL.")

    conn.close()
    print("\nALL DATABASE SETUP & MIGRATION TASKS COMPLETED SUCCESSFULLY!")

except Exception as e:
    print(f"FATAL: Database initialization error: {e}", file=sys.stderr)
    sys.exit(1)
