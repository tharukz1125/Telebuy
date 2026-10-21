import os
import sys
import json
import base64
import hashlib
import re
import urllib.parse
from datetime import datetime, date, timezone, timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer as HTTPServer
from urllib.parse import urlparse, parse_qs
import pymysql
import pymysql.cursors

# ============================================================
# 1. ENVIRONMENT VARIABLES CONFIGURATION
# ============================================================
ENV_FILE = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(ENV_FILE):
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

PORT = int(os.environ.get('PORT', 3000))
BASE_URL = os.environ.get('BASE_URL', f'http://localhost:{PORT}')

# Database Configuration (MySQL)
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_NAME = os.environ.get('DB_NAME', 'telebuy_db')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

# PayHere Configuration
MERCHANT_ID = os.environ.get('MERCHANT_ID', '1238371')
MERCHANT_SECRET = os.environ.get('MERCHANT_SECRET', 'NDE2Njk4MTMzNzE3ODQzNjI3NjMzNzQ0NjI1MTAyMzgwNTM1MzgwNA==')
ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'telebuy_admin_secret_2026')
PAYHERE_MODE = os.environ.get('PAYHERE_MODE', 'sandbox').lower()

PAYHERE_ACTION_URL = (
    'https://www.payhere.lk/pay/checkout'
    if PAYHERE_MODE == 'live'
    else 'https://sandbox.payhere.lk/pay/checkout'
)

# 7 Official Delivery Stages (as requested in Requirement 4)
VALID_DELIVERY_STAGES = [
    "Order Placed",
    "Payment Confirmed",
    "Processing",
    "Packed",
    "Shipped",
    "Out for Delivery",
    "Delivered"
]

# ============================================================
# 2. MYSQL DATABASE CONNECTION & INITIALIZATION
# ============================================================
def get_db_connection():
    """
    Connects to the persistent MySQL database using environment variables.
    Strictly raises an error if MySQL is unreachable, adhering to no-mock/no-fallback rule.
    """
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return conn
    except Exception as err:
        print(f"[TeleBuy DB Error] Could not connect to MySQL at {DB_HOST}:{DB_PORT}/{DB_NAME}: {err}")
        raise err

def initialize_database():
    """Ensures database tables and initial seed data exist in MySQL."""
    try:
        # 1. Connect without DB name to guarantee database creation
        admin_conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        with admin_conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        admin_conn.commit()
        admin_conn.close()

        # 2. Apply schema.sql
        conn = get_db_connection()
        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            with conn.cursor() as cur:
                statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
                for stmt in statements:
                    cur.execute(stmt)
            conn.commit()

        # 3. Apply seed.sql
        seed_path = os.path.join(os.path.dirname(__file__), 'database', 'seed.sql')
        if os.path.exists(seed_path):
            with open(seed_path, 'r', encoding='utf-8') as f:
                seed_sql = f.read()
            with conn.cursor() as cur:
                statements = [s.strip() for s in seed_sql.split(';') if s.strip()]
                for stmt in statements:
                    cur.execute(stmt)
            conn.commit()
        conn.close()
        print(f"[TeleBuy Database] Connected and verified MySQL database: `{DB_NAME}`.")
    except Exception as e:
        print(f"[TeleBuy Database WARNING] Could not auto-initialize MySQL: {e}")
        print("Please ensure MySQL is running on port 3306 or run: python database/init_and_migrate.py")

initialize_database()

# ============================================================
# 3. HELPER FUNCTIONS & CRYPTOGRAPHY
# ============================================================
def generate_payhere_hash(merchant_id, order_id, amount_formatted, currency, merchant_secret):
    """
    Official PayHere MD5 Hashing Formula:
    secret_hash = UPPERCASE(MD5(merchant_secret))
    hash = UPPERCASE(MD5(merchant_id + order_id + amount + currency + secret_hash))
    """
    secret_hash = hashlib.md5(merchant_secret.encode('utf-8')).hexdigest().upper()
    combined_str = f"{merchant_id}{order_id}{amount_formatted}{currency}{secret_hash}"
    return hashlib.md5(combined_str.encode('utf-8')).hexdigest().upper()

def calculate_estimated_delivery(days_offset=3):
    future_date = datetime.now() + timedelta(days=days_offset)
    return future_date.strftime("%A, %B %d, %Y")

def hash_user_password(password):
    salted = (password + "_telebuy_salt_2026").encode('utf-8')
    return hashlib.sha256(salted).hexdigest()

def create_jwt_session(user_row, remember_me=True):
    session_duration_ms = 7 * 24 * 60 * 60 * 1000 if remember_me else 24 * 60 * 60 * 1000
    expires_at = int(datetime.now().timestamp() * 1000) + session_duration_ms
    header_b64 = base64.b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip('=')
    payload = json.dumps({
        'sub': user_row['user_id'],
        'id': user_row['id'],
        'email': user_row['email'],
        'role': user_row['role'],
        'exp': expires_at
    })
    payload_b64 = base64.b64encode(payload.encode()).decode().rstrip('=')
    sig = hashlib.sha256(f"{header_b64}.{payload_b64}.{ADMIN_SECRET_KEY}".encode()).hexdigest()
    token = f"tb_jwt_{header_b64}.{payload_b64}.{sig}"
    return token, expires_at

def fetch_full_order(order_id_or_code):
    """
    Fetches complete order record, items, delivery history, and payments from MySQL.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as c:
            c.execute('SELECT * FROM orders WHERE order_id = %s OR id = %s', (
                order_id_or_code,
                int(order_id_or_code) if str(order_id_or_code).isdigit() else -1
            ))
            order_row = c.fetchone()
            if not order_row:
                return None
            
            order_dict = dict(order_row)
            order_pk = order_dict['id']
            
            # Format decimals
            for f in ['subtotal', 'delivery_fee', 'total_amount']:
                if order_dict.get(f) is not None:
                    order_dict[f] = float(order_dict[f])
            
            # Format datetimes
            for f in ['created_at', 'updated_at']:
                if isinstance(order_dict.get(f), (datetime, date)):
                    order_dict[f] = order_dict[f].isoformat()

            # Parse shipping address
            try:
                if isinstance(order_dict.get('shipping_address'), str) and order_dict['shipping_address'].strip().startswith('{'):
                    order_dict['shipping_address_obj'] = json.loads(order_dict['shipping_address'])
                else:
                    order_dict['shipping_address_obj'] = {
                        'street': order_dict.get('shipping_address', ''),
                        'city': 'Colombo',
                        'postalCode': '00300'
                    }
            except Exception:
                order_dict['shipping_address_obj'] = {'street': str(order_dict.get('shipping_address', ''))}

            # Fetch order items
            c.execute('SELECT * FROM order_items WHERE order_id = %s', (order_pk,))
            items_rows = c.fetchall()
            order_items = []
            for r in items_rows:
                it = dict(r)
                it['unit_price'] = float(it['unit_price'])
                it['line_total'] = float(it['line_total'])
                order_items.append(it)
            order_dict['items'] = order_items

            # Fetch delivery history timeline from order_status_history
            c.execute('SELECT * FROM order_status_history WHERE order_id = %s ORDER BY id ASC', (order_pk,))
            hist_rows = c.fetchall()
            history_list = []
            for h in hist_rows:
                hd = dict(h)
                if isinstance(hd.get('timestamp'), (datetime, date)):
                    hd['timestamp'] = hd['timestamp'].isoformat()
                history_list.append(hd)
            order_dict['delivery_history'] = history_list

            # Fetch payments
            c.execute('SELECT * FROM payments WHERE order_id = %s ORDER BY id ASC', (order_pk,))
            pay_rows = c.fetchall()
            payments_list = []
            for p in pay_rows:
                pd = dict(p)
                pd['amount'] = float(pd['amount'])
                if isinstance(pd.get('created_at'), (datetime, date)):
                    pd['created_at'] = pd['created_at'].isoformat()
                payments_list.append(pd)
            order_dict['payments'] = payments_list

            # 7-stage progress stepper
            history_stages_map = {h['stage']: h for h in history_list}
            current_stage = order_dict['delivery_status']
            current_stage_idx = VALID_DELIVERY_STAGES.index(current_stage) if current_stage in VALID_DELIVERY_STAGES else 0

            stages_summary = []
            for idx, stage_name in enumerate(VALID_DELIVERY_STAGES):
                hist_entry = history_stages_map.get(stage_name)
                is_completed = idx < current_stage_idx or (stage_name == current_stage and current_stage == "Delivered")
                is_current = (stage_name == current_stage and current_stage != "Delivered") or (stage_name == "Delivered" and current_stage == "Delivered")
                
                stages_summary.append({
                    'stage': stage_name,
                    'index': idx + 1,
                    'completed': bool(is_completed or hist_entry),
                    'current': is_current,
                    'timestamp': hist_entry['timestamp'] if hist_entry else None,
                    'description': hist_entry['description'] if hist_entry else None,
                    'updated_by': hist_entry['updated_by'] if hist_entry else None
                })

            order_dict['tracking_stages'] = stages_summary
            order_dict['stages'] = stages_summary
            order_dict['id'] = order_dict['order_id']
            order_dict['amount'] = order_dict['total_amount']
            order_dict['formattedAmount'] = f"{order_dict['total_amount']:.2f}"
            order_dict['createdAt'] = order_dict['created_at']
            order_dict['updatedAt'] = order_dict['updated_at']
            order_dict['paymentStatus'] = order_dict['payment_status']
            order_dict['orderStatus'] = order_dict['order_status']
            order_dict['deliveryStatus'] = order_dict['delivery_status']
            order_dict['delivery_stage'] = order_dict['delivery_status']
            order_dict['deliveryStage'] = order_dict['delivery_status']

            # Customer compatibility object
            order_dict['customer'] = {
                'name': order_dict['customer_name'],
                'firstName': order_dict['customer_name'].split(' ')[0],
                'lastName': ' '.join(order_dict['customer_name'].split(' ')[1:]),
                'email': order_dict['customer_email'],
                'phone': order_dict['customer_phone'],
                'address': order_dict['shipping_address_obj'].get('street', ''),
                'city': order_dict['shipping_address_obj'].get('city', ''),
                'postalCode': order_dict['shipping_address_obj'].get('postalCode', ''),
                'notes': order_dict.get('delivery_notes', '')
            }

            return order_dict
    finally:
        conn.close()

# ============================================================
# 4. HTTP REQUEST HANDLER WITH MYSQL BACKEND
# ============================================================
import decimal

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

class TeleBuyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Token, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=json_serial).encode('utf-8'))

    def check_admin_auth(self):
        token = self.headers.get('X-Admin-Token', '')
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ', 1)[1].strip()
        return bool(token and token == ADMIN_SECRET_KEY)

    # --------------------------------------------------------
    # GET ROUTE HANDLER
    # --------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. Health & Database Verification
        if path == '/api/health':
            try:
                conn = get_db_connection()
                counts = {}
                with conn.cursor() as cur:
                    for tbl in ['products', 'categories', 'orders', 'users']:
                        cur.execute(f"SELECT COUNT(*) AS c FROM `{tbl}`")
                        counts[tbl] = cur.fetchone()['c']
                conn.close()
                self.send_json(200, {
                    'status': 'ONLINE',
                    'store': 'TeleBuy.lk',
                    'gateway': 'PayHere',
                    'merchant_id': MERCHANT_ID,
                    'mode': PAYHERE_MODE,
                    'db': 'mysql',
                    'db_name': DB_NAME,
                    'records': counts
                })
            except Exception as e:
                self.send_json(500, {
                    'status': 'DEGRADED',
                    'error': f"MySQL database connection failed: {e}. Please ensure MySQL is running on {DB_HOST}:{DB_PORT}."
                })
            return

        # 2. Get Categories: GET /api/categories
        if path == '/api/categories':
            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM categories ORDER BY display_order ASC, id ASC")
                    rows = cur.fetchall()
                conn.close()
                self.send_json(200, {'success': True, 'categories': rows})
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Database query failed: {e}"})
            return

        # 3. Get Products: GET /api/products
        if path == '/api/products':
            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    sql = """
                        SELECT p.*, c.slug AS category_slug, c.name AS category_name
                        FROM products p
                        LEFT JOIN categories c ON p.category_id = c.id
                        WHERE 1=1
                    """
                    params = []
                    cat = query.get('category', [''])[0].strip().lower()
                    if cat:
                        sql += " AND (c.slug = %s OR p.product_id LIKE %s)"
                        params.extend([cat, f"{cat}-%"])
                    
                    feat = query.get('featured', [''])[0].strip().lower()
                    if feat in ['true', '1']:
                        sql += " AND p.is_featured = 1"
                    
                    brand = query.get('brand', [''])[0].strip()
                    if brand:
                        sql += " AND p.brand = %s"
                        params.append(brand)
                    
                    q = query.get('q', query.get('search', ['']))[0].strip()
                    if q:
                        sql += " AND (p.title LIKE %s OR p.brand LIKE %s OR p.description LIKE %s)"
                        like_term = f"%{q}%"
                        params.extend([like_term, like_term, like_term])
                    
                    sql += " ORDER BY p.is_featured DESC, p.id ASC"
                    cur.execute(sql, params)
                    rows = cur.fetchall()

                    products = []
                    for r in rows:
                        p = dict(r)
                        p['price'] = float(p['price'])
                        p['priceNum'] = p['price']
                        p['rating_score'] = float(p['rating_score'])
                        for f in ['created_at', 'updated_at']:
                            if isinstance(p.get(f), (datetime, date)):
                                p[f] = p[f].isoformat()
                        products.append(p)

                conn.close()
                self.send_json(200, {'success': True, 'products': products, 'count': len(products)})
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Database query failed: {e}"})
            return

        # 4. Get Single Product by Product ID: GET /api/products/:productId
        prod_match = re.match(r'^/api/products/([^/]+)$', path)
        if prod_match:
            pid = prod_match.group(1)
            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.*, c.slug AS category_slug, c.name AS category_name
                        FROM products p
                        LEFT JOIN categories c ON p.category_id = c.id
                        WHERE p.product_id = %s OR p.id = %s
                    """, (pid, int(pid) if pid.isdigit() else -1))
                    row = cur.fetchone()
                conn.close()
                if not row:
                    self.send_json(404, {'success': False, 'message': f"Product '{pid}' not found."})
                    return
                p = dict(row)
                p['price'] = float(p['price'])
                p['priceNum'] = p['price']
                p['rating_score'] = float(p['rating_score'])
                for f in ['created_at', 'updated_at']:
                    if isinstance(p.get(f), (datetime, date)):
                        p[f] = p[f].isoformat()
                self.send_json(200, {'success': True, 'product': p})
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Database query failed: {e}"})
            return

        # 5. Get Single Order by Order ID: GET /api/orders/:orderId
        order_match = re.match(r'^/api/orders/([^/]+)$', path)
        if order_match:
            order_id = order_match.group(1)
            try:
                order_data = fetch_full_order(order_id)
                if not order_data:
                    self.send_json(404, {'success': False, 'message': 'Order not found.'})
                    return
                self.send_json(200, {
                    'success': True,
                    'order': order_data,
                    'stages': order_data.get('tracking_stages', [])
                })
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Database query failed: {e}"})
            return

        # 6. Customer Order History: GET /api/customer/orders?email=...&customerId=...
        if path == '/api/customer/orders':
            email = (query.get('email', [''])[0]).strip().lower()
            customer_id = (query.get('customerId', [''])[0]).strip()
            
            if not email and not customer_id:
                self.send_json(400, {'success': False, 'message': 'Please provide customer email or account ID.'})
                return
            
            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    if customer_id and email:
                        cur.execute("SELECT order_id FROM orders WHERE user_id = %s OR LOWER(customer_email) = %s ORDER BY id DESC", (customer_id, email))
                    elif customer_id:
                        cur.execute("SELECT order_id FROM orders WHERE user_id = %s ORDER BY id DESC", (customer_id,))
                    else:
                        cur.execute("SELECT order_id FROM orders WHERE LOWER(customer_email) = %s ORDER BY id DESC", (email,))
                    rows = cur.fetchall()
                conn.close()

                orders = []
                for r in rows:
                    ord_item = fetch_full_order(r['order_id'])
                    if ord_item:
                        orders.append(ord_item)

                self.send_json(200, {'success': True, 'orders': orders, 'count': len(orders)})
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Database query failed: {e}"})
            return

        # 7. Admin Order List: GET /api/admin/orders
        if path == '/api/admin/orders':
            if not self.check_admin_auth():
                self.send_json(401, {'success': False, 'message': 'Unauthorized admin access. Invalid admin credentials.'})
                return
            
            status_filter = query.get('status', [''])[0].strip()
            search_query = query.get('search', [''])[0].strip()
            
            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    sql = 'SELECT order_id FROM orders'
                    conditions = []
                    params = []

                    if status_filter and status_filter.lower() != 'all':
                        conditions.append('(payment_status = %s OR delivery_status = %s)')
                        params.extend([status_filter, status_filter])

                    if search_query:
                        conditions.append('(order_id LIKE %s OR customer_name LIKE %s OR customer_email LIKE %s OR customer_phone LIKE %s OR tracking_number LIKE %s)')
                        like_term = f"%{search_query}%"
                        params.extend([like_term, like_term, like_term, like_term, like_term])

                    if conditions:
                        sql += ' WHERE ' + ' AND '.join(conditions)

                    sql += ' ORDER BY id DESC'
                    cur.execute(sql, params)
                    rows = cur.fetchall()
                conn.close()

                orders = []
                for r in rows:
                    ord_item = fetch_full_order(r['order_id'])
                    if ord_item:
                        orders.append(ord_item)

                self.send_json(200, {'success': True, 'orders': orders, 'count': len(orders)})
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Database query failed: {e}"})
            return

        # 8. User Info: GET /api/auth/me
        if path == '/api/auth/me':
            auth_header = self.headers.get('Authorization', '')
            token = auth_header.split('Bearer ', 1)[1].strip() if auth_header.startswith('Bearer ') else ''
            if not token:
                self.send_json(401, {'success': False, 'message': 'Not authenticated.'})
                return
            try:
                parts = token.replace('tb_jwt_', '').split('.')
                payload = json.loads(base64.b64decode(parts[1] + '==').decode())
                user_id = payload.get('sub')
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT u.*, a.street, a.city, a.state, a.postal_code, a.country FROM users u LEFT JOIN shipping_addresses a ON u.id = a.user_id WHERE u.user_id = %s", (user_id,))
                    user = cur.fetchone()
                conn.close()
                if not user:
                    self.send_json(404, {'success': False, 'message': 'User account not found.'})
                    return
                user.pop('password_hash', None)
                self.send_json(200, {'success': True, 'user': user})
            except Exception as e:
                self.send_json(401, {'success': False, 'message': 'Invalid session token.'})
            return

        # Fallback to standard static file server
        super().do_GET()

    # --------------------------------------------------------
    # POST ROUTE HANDLER
    # --------------------------------------------------------
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''

        # 1. User Registration: POST /api/auth/register
        if path == '/api/auth/register':
            try:
                body = json.loads(post_data.decode('utf-8'))
                full_name = (body.get('fullName') or body.get('full_name') or body.get('name') or '').strip()
                email = (body.get('email') or '').strip().lower()
                password = (body.get('password') or '').strip()
                phone = (body.get('phone') or '').strip()
                role = (body.get('role') or 'customer').strip()

                if not full_name or len(full_name) < 2:
                    self.send_json(400, {'success': False, 'message': 'Please provide your full name (at least 2 characters).'})
                    return
                if not email or '@' not in email:
                    self.send_json(400, {'success': False, 'message': 'Please provide a valid email address.'})
                    return
                if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
                    self.send_json(400, {'success': False, 'message': 'Password must be at least 8 characters long and contain uppercase, lowercase, and numeric characters.'})
                    return

                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                    if cur.fetchone():
                        conn.close()
                        self.send_json(400, {'success': False, 'message': 'An account with this email address is already registered.'})
                        return

                    pw_hash = hash_user_password(password)
                    user_uid = f"usr_{int(datetime.now().timestamp() * 1000)}"
                    avatar = f"https://api.dicebear.com/7.x/bottts/svg?seed={urllib.parse.quote(full_name)}"

                    cur.execute("""
                        INSERT INTO users (user_id, full_name, email, password_hash, role, phone, avatar)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (user_uid, full_name, email, pw_hash, role, phone, avatar))
                    user_pk = cur.lastrowid

                    cur.execute("""
                        INSERT INTO shipping_addresses (user_id, recipient_name, phone, street, city, state, postal_code, country, is_default)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
                    """, (user_pk, full_name, phone, '', 'Colombo', 'Western Province', '00300', 'Sri Lanka'))

                conn.commit()
                conn.close()

                self.send_json(201, {
                    'success': True,
                    'message': 'Registration successful! You can now log in.',
                    'user': {
                        'id': user_pk,
                        'user_id': user_uid,
                        'full_name': full_name,
                        'email': email,
                        'role': role,
                        'phone': phone,
                        'avatar': avatar
                    }
                })
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Registration failed: {e}"})
            return

        # 2. User Login: POST /api/auth/login
        if path == '/api/auth/login':
            try:
                body = json.loads(post_data.decode('utf-8'))
                email = (body.get('email') or '').strip().lower()
                password = (body.get('password') or '').strip()
                remember_me = bool(body.get('rememberMe', True))

                GENERIC_ERROR = "Invalid email or password. Please check your credentials and try again."

                if not email or not password:
                    self.send_json(400, {'success': False, 'message': GENERIC_ERROR})
                    return

                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                    user = cur.fetchone()

                    if not user:
                        conn.close()
                        self.send_json(401, {'success': False, 'message': GENERIC_ERROR})
                        return

                    if hash_user_password(password) != user['password_hash']:
                        conn.close()
                        self.send_json(401, {'success': False, 'message': GENERIC_ERROR})
                        return

                    cur.execute("SELECT * FROM shipping_addresses WHERE user_id = %s ORDER BY is_default DESC LIMIT 1", (user['id'],))
                    addr = cur.fetchone()

                conn.close()

                token, expires_at = create_jwt_session(user, remember_me)
                user_payload = {
                    'id': user['id'],
                    'user_id': user['user_id'],
                    'full_name': user['full_name'],
                    'email': user['email'],
                    'role': user['role'],
                    'phone': user.get('phone', ''),
                    'avatar': user.get('avatar', ''),
                    'address': addr.get('street', '') if addr else '',
                    'city': addr.get('city', '') if addr else 'Colombo',
                    'state': addr.get('state', '') if addr else 'Western Province',
                    'postalCode': addr.get('postal_code', '') if addr else '00300',
                    'country': addr.get('country', 'Sri Lanka') if addr else 'Sri Lanka'
                }

                self.send_json(200, {
                    'success': True,
                    'message': f"Welcome back, {user['full_name']}!",
                    'token': token,
                    'user': user_payload,
                    'session': {
                        'token': token,
                        'user': user_payload,
                        'expires_at': expires_at
                    }
                })
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Login failed: {e}"})
            return

        # 3. User Logout: POST /api/auth/logout
        if path == '/api/auth/logout':
            self.send_json(200, {'success': True, 'message': 'Logged out successfully.'})
            return

        # 4. Initiate Payment (PayHere OR Cash on Delivery): POST /api/checkout/initiate-payment
        if path == '/api/checkout/initiate-payment':
            try:
                body = json.loads(post_data.decode('utf-8'))
                customer = body.get('customer') or {}
                items = body.get('items') or []
                payment_method = (body.get('paymentMethod') or body.get('payment_method') or 'payhere').lower().strip()
                customer_id = body.get('customerId') or body.get('user_id')

                if not items or not isinstance(items, list) or len(items) == 0:
                    self.send_json(400, {'success': False, 'error': 'Your shopping cart is empty.'})
                    return

                first_name = (customer.get('firstName') or customer.get('first_name') or '').strip()
                last_name = (customer.get('lastName') or customer.get('last_name') or '').strip()
                full_name = f"{first_name} {last_name}".strip() or customer.get('name', 'Valued Customer')
                email = (customer.get('email') or '').strip().lower()
                phone = (customer.get('phone') or '').strip()
                address = (customer.get('address') or '').strip()
                city = (customer.get('city') or '').strip()
                postal_code = (customer.get('postalCode') or customer.get('postal_code') or '00300').strip()
                notes = (customer.get('notes') or customer.get('deliveryNotes') or customer.get('delivery_notes') or '').strip()

                if not first_name or not email or not phone or not address or not city:
                    self.send_json(400, {'success': False, 'error': 'Please provide all required shipping and contact details.'})
                    return

                if payment_method not in ['payhere', 'cod']:
                    self.send_json(400, {'success': False, 'error': 'Invalid payment method selected. Choose PayHere or Cash on Delivery.'})
                    return

                # Connect to MySQL and retrieve live prices & stock
                conn = get_db_connection()
                validated_items = []
                subtotal = 0.0

                with conn.cursor() as cur:
                    for it in items:
                        prod_id = it.get('id')
                        qty = max(1, int(it.get('qty') or it.get('quantity') or 1))

                        # Query MySQL products table directly
                        cur.execute("SELECT * FROM products WHERE product_id = %s OR id = %s", (
                            prod_id,
                            int(prod_id) if str(prod_id).isdigit() else -1
                        ))
                        db_prod = cur.fetchone()

                        if not db_prod:
                            conn.close()
                            self.send_json(400, {'success': False, 'error': f"Product '{prod_id}' is unavailable."})
                            return

                        price = float(db_prod['price'])
                        title = db_prod['title']
                        brand = db_prod['brand']
                        image = db_prod['image']

                        line_total = price * qty
                        subtotal += line_total
                        validated_items.append({
                            'product_id': db_prod['product_id'],
                            'title': title,
                            'brand': brand,
                            'image': image,
                            'qty': qty,
                            'unit_price': price,
                            'line_total': line_total
                        })

                    delivery_fee = 0.0
                    total_amount = subtotal + delivery_fee
                    formatted_amount = f"{total_amount:.2f}"
                    currency = 'LKR'

                    # Find user ID primary key if registered
                    user_pk = None
                    if customer_id:
                        cur.execute("SELECT id FROM users WHERE user_id = %s OR id = %s", (
                            customer_id,
                            int(customer_id) if str(customer_id).isdigit() else -1
                        ))
                        u_row = cur.fetchone()
                        if u_row:
                            user_pk = u_row['id']
                    if not user_pk and email:
                        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                        u_row = cur.fetchone()
                        if u_row:
                            user_pk = u_row['id']

                    # Generate Unique Order ID (TB-YYYY-XXXXX)
                    random_suffix = int(datetime.now().timestamp() * 1000) % 90000 + 10000
                    order_id = f"TB-{datetime.now().year}-{random_suffix}"
                    now_dt = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    est_delivery = calculate_estimated_delivery(3)
                    shipping_addr_json = json.dumps({
                        'street': address,
                        'city': city,
                        'postalCode': postal_code,
                        'country': 'Sri Lanka'
                    })

                    # Status configurations
                    is_cod = (payment_method == 'cod')
                    pay_status = 'PENDING_COD' if is_cod else 'PENDING'
                    ord_status = 'Order Confirmed' if is_cod else 'Pending Payment'
                    deliv_status = 'Payment Confirmed' if is_cod else 'Order Placed'

                    # Insert Master Order into MySQL
                    insert_order_sql = """
                        INSERT INTO orders (
                            order_id, user_id, customer_name, customer_email, customer_phone,
                            shipping_address, subtotal, delivery_fee, total_amount, currency,
                            payment_method, payment_status, order_status, delivery_status,
                            estimated_delivery, delivery_notes, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """
                    cur.execute(insert_order_sql, (
                        order_id, user_pk, full_name, email, phone,
                        shipping_addr_json, subtotal, delivery_fee, total_amount, currency,
                        payment_method, pay_status, ord_status, deliv_status,
                        est_delivery, notes, now_dt, now_dt
                    ))
                    order_pk = cur.lastrowid

                    # Insert Line Items into MySQL
                    for v_item in validated_items:
                        cur.execute("""
                            INSERT INTO order_items (
                                order_id, product_id, title, brand, image, qty, unit_price, line_total
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            order_pk, v_item['product_id'], v_item['title'], v_item['brand'],
                            v_item['image'], v_item['qty'], v_item['unit_price'], v_item['line_total']
                        ))

                    # Insert Initial Delivery History Stage
                    cur.execute("""
                        INSERT INTO order_status_history (order_id, stage, description, updated_by, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_pk, 'Order Placed', 'Order placed by customer.', 'System', now_dt))

                    if is_cod:
                        cur.execute("""
                            INSERT INTO order_status_history (order_id, stage, description, updated_by, timestamp)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (order_pk, 'Payment Confirmed', 'Cash on Delivery terms accepted. Payment will be collected upon delivery.', 'System', now_dt))

                    conn.commit()

                conn.close()

                # Response for COD
                if is_cod:
                    full_order_record = fetch_full_order(order_id)
                    self.send_json(200, {
                        'success': True,
                        'orderId': order_id,
                        'order_id': order_id,
                        'order': full_order_record,
                        'paymentMethod': 'cod',
                        'payment_method': 'cod',
                        'message': 'Order placed successfully with Cash on Delivery.',
                        'redirectUrl': f"order-confirmation.html?order_id={order_id}&status=cod_success"
                    })
                    return

                # PayHere Cryptographic Hash Generation
                hash_value = generate_payhere_hash(
                    MERCHANT_ID,
                    order_id,
                    formatted_amount,
                    currency,
                    MERCHANT_SECRET
                )

                item_summary = ', '.join([f"{item['title']} (x{item['qty']})" for item in validated_items])
                if len(item_summary) > 200:
                    item_summary = item_summary[:197] + '...'

                payhere_params = {
                    'merchant_id': MERCHANT_ID,
                    'return_url': f"{BASE_URL}/order-confirmation.html?order_id={order_id}&status=success",
                    'cancel_url': f"{BASE_URL}/order-confirmation.html?order_id={order_id}&status=cancelled",
                    'notify_url': f"{BASE_URL}/api/checkout/notify",
                    'order_id': order_id,
                    'items': item_summary or 'TeleBuy Smart TV Order',
                    'currency': currency,
                    'amount': formatted_amount,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'city': city,
                    'country': 'Sri Lanka',
                    'hash': hash_value
                }

                self.send_json(200, {
                    'success': True,
                    'orderId': order_id,
                    'order_id': order_id,
                    'paymentMethod': 'payhere',
                    'payment_method': 'payhere',
                    'paymentUrl': PAYHERE_ACTION_URL,
                    'actionUrl': PAYHERE_ACTION_URL,
                    'params': payhere_params,
                    'payhereData': payhere_params,
                    'payhere_payload': payhere_params
                })
            except Exception as e:
                self.send_json(500, {'success': False, 'error': f"Payment initiation failed: {e}"})
            return

        # 5. Retry Payment for Existing Pending Order: POST /api/orders/:orderId/retry-payment
        retry_match = re.match(r'^/api/orders/([^/]+)/retry-payment$', path)
        if retry_match:
            order_id = retry_match.group(1)
            try:
                order_data = fetch_full_order(order_id)
                if not order_data:
                    self.send_json(404, {'success': False, 'message': 'Order not found.'})
                    return

                formatted_amount = f"{float(order_data['total_amount']):.2f}"
                hash_value = generate_payhere_hash(
                    MERCHANT_ID,
                    order_id,
                    formatted_amount,
                    order_data['currency'],
                    MERCHANT_SECRET
                )

                customer = order_data.get('customer', {})
                item_titles = ', '.join([f"{it['title']} (x{it['qty']})" for it in order_data.get('items', [])])
                if len(item_titles) > 200:
                    item_titles = item_titles[:197] + '...'

                payhere_params = {
                    'merchant_id': MERCHANT_ID,
                    'return_url': f"{BASE_URL}/order-confirmation.html?order_id={order_id}&status=success",
                    'cancel_url': f"{BASE_URL}/order-confirmation.html?order_id={order_id}&status=cancelled",
                    'notify_url': f"{BASE_URL}/api/checkout/notify",
                    'order_id': order_id,
                    'items': item_titles or 'TeleBuy Smart TV Order',
                    'currency': order_data['currency'],
                    'amount': formatted_amount,
                    'first_name': customer.get('firstName', 'Valued'),
                    'last_name': customer.get('lastName', 'Customer'),
                    'email': customer.get('email', order_data['customer_email']),
                    'phone': customer.get('phone', order_data['customer_phone']),
                    'address': customer.get('address', 'Galle Road'),
                    'city': customer.get('city', 'Colombo'),
                    'country': 'Sri Lanka',
                    'hash': hash_value
                }

                self.send_json(200, {
                    'success': True,
                    'orderId': order_id,
                    'order_id': order_id,
                    'paymentUrl': PAYHERE_ACTION_URL,
                    'actionUrl': PAYHERE_ACTION_URL,
                    'params': payhere_params,
                    'payhereData': payhere_params,
                    'payhere_payload': payhere_params
                })
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Payment retry failed: {e}"})
            return

        # 6. PayHere IPN Webhook: POST /api/checkout/notify
        if path == '/api/checkout/notify':
            raw_str = post_data.decode('utf-8')
            body_dict = {}
            is_json_req = False
            try:
                body_dict = json.loads(raw_str)
                is_json_req = True
            except Exception:
                try:
                    parsed_body = parse_qs(raw_str)
                    body_dict = {k: v[0] for k, v in parsed_body.items()}
                except Exception:
                    body_dict = {}

            order_id = body_dict.get('order_id')
            payment_id = body_dict.get('payment_id') or body_dict.get('payhere_payment_id') or 'N/A'
            payhere_amount = str(body_dict.get('payhere_amount') or '')
            payhere_currency = str(body_dict.get('payhere_currency') or '')
            status_code = str(body_dict.get('status_code') or '')
            md5sig = (body_dict.get('md5sig') or '').strip().upper()
            method = body_dict.get('method', 'ONLINE')

            print(f"[TeleBuy IPN] Webhook incoming: order_id={order_id}, status_code={status_code}, payment_id={payment_id}")

            # Cryptographic Signature Verification
            secret_hash = hashlib.md5(MERCHANT_SECRET.encode('utf-8')).hexdigest().upper()
            local_combined = f"{MERCHANT_ID}{order_id}{payhere_amount}{payhere_currency}{status_code}{secret_hash}"
            expected_md5sig = hashlib.md5(local_combined.encode('utf-8')).hexdigest().upper()

            if expected_md5sig != md5sig:
                print(f"[TeleBuy IPN] REJECTED: MD5 Signature mismatch for order {order_id}.")
                if is_json_req:
                    self.send_json(400, {'success': False, 'error': 'Signature Verification Failed'})
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Signature Verification Failed")
                return

            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
                    order_row = cur.fetchone()

                    if not order_row:
                        conn.close()
                        if is_json_req:
                            self.send_json(404, {'success': False, 'error': 'Order Not Found'})
                        else:
                            self.send_response(404)
                            self.end_headers()
                            self.wfile.write(b"Order Not Found")
                        return

                    order_pk = order_row['id']
                    current_pay_status = order_row['payment_status']
                    now_dt = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

                    # Idempotency Protection: If already PAID, acknowledge without re-processing
                    if current_pay_status == 'PAID' and status_code == '2':
                        print(f"[TeleBuy IPN] Idempotent hit: Order {order_id} is already marked as PAID.")
                        conn.close()
                        if is_json_req:
                            self.send_json(200, {'success': True, 'already_processed': True, 'message': 'OK (Already processed)'})
                        else:
                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(b"OK (Already processed)")
                        return

                    # Record payment in payments table
                    status_name_map = {'2': 'SUCCESS', '0': 'PENDING', '-1': 'CANCELLED', '-2': 'FAILED'}
                    cur.execute("""
                        INSERT INTO payments (order_id, payment_id, method, amount, currency, status_code, status_name, raw_response, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        order_pk, payment_id, method, float(payhere_amount or order_row['total_amount']),
                        payhere_currency or 'LKR', status_code, status_name_map.get(status_code, 'UNKNOWN'),
                        raw_str, now_dt
                    ))

                    # Process Status Codes
                    if status_code == '2':
                        cur.execute("""
                            UPDATE orders
                            SET payment_status = 'PAID',
                                order_status = 'Order Confirmed',
                                delivery_status = CASE WHEN delivery_status = 'Order Placed' THEN 'Payment Confirmed' ELSE delivery_status END,
                                payhere_payment_id = %s,
                                updated_at = %s
                            WHERE id = %s
                        """, (payment_id, now_dt, order_pk))

                        cur.execute("""
                            INSERT INTO order_status_history (order_id, stage, description, updated_by, timestamp)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (order_pk, 'Payment Confirmed', f"PayHere payment verified successfully. Transaction Ref: {payment_id}", 'PayHere Gateway', now_dt))

                    elif status_code == '-1':
                        cur.execute("UPDATE orders SET payment_status = 'CANCELLED', updated_at = %s WHERE id = %s", (now_dt, order_pk))
                        cur.execute("""
                            INSERT INTO order_status_history (order_id, stage, description, updated_by, timestamp)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (order_pk, 'Order Placed', 'Payment transaction was cancelled by customer at payment portal.', 'PayHere Gateway', now_dt))

                    elif status_code == '-2':
                        cur.execute("UPDATE orders SET payment_status = 'FAILED', updated_at = %s WHERE id = %s", (now_dt, order_pk))
                        cur.execute("""
                            INSERT INTO order_status_history (order_id, stage, description, updated_by, timestamp)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (order_pk, 'Order Placed', 'Payment transaction was declined or failed at gateway.', 'PayHere Gateway', now_dt))

                    conn.commit()
                conn.close()

                print(f"[TeleBuy IPN] SUCCESS: Order {order_id} updated with status code {status_code}.")
                if is_json_req:
                    self.send_json(200, {'success': True, 'status': 'success', 'message': 'OK'})
                else:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"OK")
            except Exception as e:
                print(f"[TeleBuy IPN] Error processing notification: {e}")
                self.send_json(500, {'success': False, 'error': f"Notification error: {e}"})
            return

        # 7. Admin Update Delivery Status: POST /api/admin/orders/:orderId/delivery-status
        admin_deliv_match = re.match(r'^/api/admin/orders/([^/]+)/delivery-status$', path)
        if admin_deliv_match:
            if not self.check_admin_auth():
                self.send_json(401, {'success': False, 'message': 'Unauthorized admin request.'})
                return

            order_id = admin_deliv_match.group(1)
            try:
                body = json.loads(post_data.decode('utf-8'))
            except Exception:
                body = {}

            new_stage = (body.get('deliveryStatus') or body.get('delivery_status') or body.get('stage') or '').strip()
            tracking_number = (body.get('trackingNumber') or body.get('tracking_number') or '').strip()
            courier_name = (body.get('courierName') or body.get('courier_name') or '').strip()
            note = (body.get('note') or body.get('notes') or body.get('description') or f"Status updated to '{new_stage}' by Administrator").strip()

            if new_stage not in VALID_DELIVERY_STAGES:
                self.send_json(400, {
                    'success': False,
                    'message': f"Invalid delivery stage. Must be one of: {', '.join(VALID_DELIVERY_STAGES)}"
                })
                return

            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM orders WHERE order_id = %s OR id = %s", (
                        order_id,
                        int(order_id) if order_id.isdigit() else -1
                    ))
                    ord_row = cur.fetchone()
                    if not ord_row:
                        conn.close()
                        self.send_json(404, {'success': False, 'message': f"Order '{order_id}' not found."})
                        return

                    order_pk = ord_row['id']
                    now_dt = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

                    update_sql = """
                        UPDATE orders
                        SET delivery_status = %s,
                            tracking_number = CASE WHEN %s != '' THEN %s ELSE tracking_number END,
                            courier_name = CASE WHEN %s != '' THEN %s ELSE courier_name END,
                            updated_at = %s
                        WHERE id = %s
                    """
                    cur.execute(update_sql, (new_stage, tracking_number, tracking_number, courier_name, courier_name, now_dt, order_pk))

                    cur.execute("""
                        INSERT INTO order_status_history (order_id, stage, description, updated_by, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_pk, new_stage, note, 'Administrator', now_dt))

                    conn.commit()
                conn.close()

                updated_order = fetch_full_order(order_id)
                self.send_json(200, {
                    'success': True,
                    'message': f"Order {order_id} delivery status updated to '{new_stage}'.",
                    'order': updated_order,
                    'stage': new_stage,
                    'deliveryStatus': new_stage,
                    'courier_name': updated_order.get('courier_name'),
                    'tracking_number': updated_order.get('tracking_number')
                })
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Failed to update delivery status: {e}"})
            return

        self.send_json(404, {'error': 'API endpoint not found'})

    # --------------------------------------------------------
    # PUT ROUTE HANDLER
    # --------------------------------------------------------
    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''

        # 1. Update User Profile: PUT /api/auth/profile
        if path == '/api/auth/profile':
            auth_header = self.headers.get('Authorization', '')
            token = auth_header.split('Bearer ', 1)[1].strip() if auth_header.startswith('Bearer ') else ''
            if not token:
                self.send_json(401, {'success': False, 'message': 'Not authenticated.'})
                return
            try:
                parts = token.replace('tb_jwt_', '').split('.')
                payload = json.loads(base64.b64decode(parts[1] + '==').decode())
                user_id = payload.get('sub')
                body = json.loads(post_data.decode('utf-8'))

                full_name = (body.get('fullName') or body.get('full_name') or '').strip()
                phone = (body.get('phone') or '').strip()
                street = (body.get('street') or body.get('address') or '').strip()
                city = (body.get('city') or '').strip()
                state = (body.get('state') or 'Western Province').strip()
                postal_code = (body.get('postalCode') or body.get('postal_code') or '').strip()

                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
                    u = cur.fetchone()
                    if not u:
                        conn.close()
                        self.send_json(404, {'success': False, 'message': 'User not found.'})
                        return

                    u_pk = u['id']
                    if full_name:
                        cur.execute("UPDATE users SET full_name = %s, phone = %s WHERE id = %s", (full_name, phone, u_pk))

                    cur.execute("SELECT id FROM shipping_addresses WHERE user_id = %s LIMIT 1", (u_pk,))
                    addr = cur.fetchone()
                    if addr:
                        cur.execute("""
                            UPDATE shipping_addresses
                            SET street = %s, city = %s, state = %s, postal_code = %s, phone = %s
                            WHERE id = %s
                        """, (street, city, state, postal_code, phone, addr['id']))
                    else:
                        cur.execute("""
                            INSERT INTO shipping_addresses (user_id, recipient_name, phone, street, city, state, postal_code, country, is_default)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Sri Lanka', 1)
                        """, (u_pk, full_name, phone, street, city, state, postal_code))

                    conn.commit()
                conn.close()

                self.send_json(200, {'success': True, 'message': 'Profile updated successfully in MySQL.'})
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Update failed: {e}"})
            return

        # 2. Admin Update Product: PUT /api/admin/products/:productId
        prod_update_match = re.match(r'^/api/admin/products/([^/]+)$', path)
        if prod_update_match:
            if not self.check_admin_auth():
                self.send_json(401, {'success': False, 'message': 'Unauthorized admin request.'})
                return

            prod_id = prod_update_match.group(1)
            try:
                body = json.loads(post_data.decode('utf-8'))
                price = body.get('price')
                stock = body.get('stock')
                badge = body.get('badge')

                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM products WHERE product_id = %s", (prod_id,))
                    if not cur.fetchone():
                        conn.close()
                        self.send_json(404, {'success': False, 'message': f"Product '{prod_id}' not found."})
                        return

                    updates = []
                    params = []
                    if price is not None:
                        updates.append("price = %s")
                        params.append(float(price))
                    if stock is not None:
                        updates.append("stock = %s")
                        params.append(int(stock))
                    if badge is not None:
                        updates.append("badge = %s")
                        params.append(badge)

                    if updates:
                        sql = f"UPDATE products SET {', '.join(updates)} WHERE product_id = %s"
                        params.append(prod_id)
                        cur.execute(sql, params)
                        conn.commit()
                conn.close()

                self.send_json(200, {'success': True, 'message': f"Product '{prod_id}' updated in MySQL."})
            except Exception as e:
                self.send_json(500, {'success': False, 'message': f"Failed to update product: {e}"})
            return

        self.send_json(404, {'error': 'API endpoint not found'})

# ============================================================
# 5. SERVER ENTRYPOINT
# ============================================================
if __name__ == '__main__':
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, TeleBuyHandler)
    print("============================================================")
    print("  TeleBuy.lk E-Commerce & Delivery Tracking Server (Python)")
    print(f"  Port:         http://localhost:{PORT}")
    print(f"  Database:     MySQL (Host: {DB_HOST}:{DB_PORT}, DB: {DB_NAME})")
    print(f"  Merchant ID:  {MERCHANT_ID}")
    print(f"  Mode:         {PAYHERE_MODE.upper()}")
    print(f"  Endpoint:     {PAYHERE_ACTION_URL}")
    print("============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
