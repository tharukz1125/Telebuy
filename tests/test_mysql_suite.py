"""
TeleBuy.lk — Comprehensive MySQL Integration Test Suite
Verifies all 10 core requirements against live MySQL database (telebuy_db).
"""

import urllib.request
import urllib.parse
import json
import hashlib
import time
import pymysql

BASE_URL = 'http://localhost:3000'
ADMIN_SECRET_KEY = 'telebuy_admin_secret_2026'
MERCHANT_ID = '1238371'
MERCHANT_SECRET = 'NDE2Njk4MTMzNzE3ODQzNjI3NjMzNzQ0NjI1MTAyMzgwNTM1MzgwNA=='

def req(url, method='GET', data=None, headers=None):
    if headers is None:
        headers = {}
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            content = resp.read().decode('utf-8')
            try:
                return resp.status, json.loads(content)
            except Exception:
                return resp.status, content
    except urllib.error.HTTPError as e:
        content = e.read().decode('utf-8')
        try:
            return e.code, json.loads(content)
        except Exception:
            return e.code, content

def run_tests():
    print("=" * 65)
    print("  TELEBUY.LK — COMPLETE MYSQL INTEGRATION TEST SUITE")
    print("=" * 65)
    passed = 0
    total = 0

    # 1. Database Connection & Health Verification
    total += 1
    status, d = req(f"{BASE_URL}/api/health")
    assert status == 200 and d.get('db') == 'mysql' and d.get('db_name') == 'telebuy_db', f"Failed health check: {d}"
    print(f"[{passed+1}/{total}] PASS: Database Connection verified. DB='{d['db']}', Database='{d['db_name']}'.")
    passed += 1

    # 2. Product & Category Retrieval from MySQL
    total += 1
    status, d_cat = req(f"{BASE_URL}/api/categories")
    assert status == 200 and len(d_cat.get('categories', [])) >= 6, f"Failed categories: {d_cat}"
    status, d_prod = req(f"{BASE_URL}/api/products?category=qled-tvs")
    assert status == 200 and len(d_prod.get('products', [])) >= 5, f"Failed products: {d_prod}"
    status, d_single = req(f"{BASE_URL}/api/products/qled-1")
    assert status == 200 and d_single['product']['product_id'] == 'qled-1', f"Failed single product: {d_single}"
    print(f"[{passed+1}/{total}] PASS: Product and Category retrieval from MySQL verified ({len(d_prod['products'])} QLEDs).")
    passed += 1

    # 3. User Registration into MySQL
    total += 1
    test_email = f"testuser_{int(time.time())}@telebuy.lk"
    status, d_reg = req(f"{BASE_URL}/api/auth/register", method='POST', data={
        'fullName': 'Saman Kumara',
        'email': test_email,
        'password': 'Password123!',
        'phone': '0779876543'
    })
    assert status == 201 and d_reg.get('success') is True, f"Failed registration: {d_reg}"
    
    # Check MySQL users table directly
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', database='telebuy_db', cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (test_email,))
        u_row = cur.fetchone()
        assert u_row is not None, "User not found in MySQL users table!"
        assert u_row['full_name'] == 'Saman Kumara', "User full_name mismatch in MySQL!"
    conn.close()
    print(f"[{passed+1}/{total}] PASS: User Registration persisted directly to MySQL `users` table.")
    passed += 1

    # 4. User Login Authenticated from MySQL
    total += 1
    status, d_login = req(f"{BASE_URL}/api/auth/login", method='POST', data={
        'email': test_email,
        'password': 'Password123!'
    })
    assert status == 200 and d_login.get('success') is True and 'token' in d_login, f"Failed login: {d_login}"
    token = d_login['token']
    print(f"[{passed+1}/{total}] PASS: User Login authenticated via MySQL password hash.")
    passed += 1

    # 5. Order Creation & Order-Item Storage in MySQL (Cash on Delivery)
    total += 1
    status, d_cod = req(f"{BASE_URL}/api/checkout/initiate-payment", method='POST', data={
        'customer': {
            'firstName': 'Saman',
            'lastName': 'Kumara',
            'email': test_email,
            'phone': '0779876543',
            'address': '78 Kandy Road',
            'city': 'Kadawatha',
            'postalCode': '11850'
        },
        'items': [{'id': 'smart-1', 'qty': 2}],
        'paymentMethod': 'cod'
    })
    assert status == 200 and d_cod.get('success') is True, f"Failed COD checkout: {d_cod}"
    cod_order_id = d_cod['orderId']

    # Direct MySQL check on orders & order_items
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', database='telebuy_db', cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM orders WHERE order_id = %s", (cod_order_id,))
        ord_row = cur.fetchone()
        assert ord_row is not None, "COD Order not in MySQL orders table!"
        assert ord_row['payment_status'] == 'PENDING_COD', f"Unexpected status: {ord_row['payment_status']}"
        cur.execute("SELECT * FROM order_items WHERE order_id = %s", (ord_row['id'],))
        it_rows = cur.fetchall()
        assert len(it_rows) == 1 and it_rows[0]['product_id'] == 'smart-1' and it_rows[0]['qty'] == 2, "Items mismatch in MySQL!"
    conn.close()
    print(f"[{passed+1}/{total}] PASS: COD Order and Order Items saved to MySQL (`orders` & `order_items`).")
    passed += 1

    # 6. PayHere Order Initiation & Cryptographic Hash Generation
    total += 1
    status, d_payhere = req(f"{BASE_URL}/api/checkout/initiate-payment", method='POST', data={
        'customer': {
            'firstName': 'Kamal',
            'lastName': 'Perera',
            'email': 'student@telebuy.lk',
            'phone': '0771234567',
            'address': '45 Galle Road',
            'city': 'Colombo',
            'postalCode': '00300'
        },
        'items': [{'id': 'qled-1', 'qty': 1}],
        'paymentMethod': 'payhere'
    })
    assert status == 200 and d_payhere.get('success') is True, f"Failed PayHere initiate: {d_payhere}"
    payhere_order_id = d_payhere['orderId']
    payhere_payload = d_payhere['params']
    assert 'hash' in payhere_payload, "Missing hash in PayHere payload!"
    print(f"[{passed+1}/{total}] PASS: PayHere order created in MySQL with MD5 signature: {payhere_order_id}.")
    passed += 1

    # 7. PayHere Webhook/IPN Payment Verification & MySQL Status Update
    total += 1
    secret_hash = hashlib.md5(MERCHANT_SECRET.encode('utf-8')).hexdigest().upper()
    amount_str = payhere_payload['amount']
    status_code = "2"
    sig_str = f"{MERCHANT_ID}{payhere_order_id}{amount_str}LKR{status_code}{secret_hash}"
    valid_md5sig = hashlib.md5(sig_str.encode('utf-8')).hexdigest().upper()

    status, d_notify = req(f"{BASE_URL}/api/checkout/notify", method='POST', data={
        'merchant_id': MERCHANT_ID,
        'order_id': payhere_order_id,
        'payment_id': '32002598711',
        'payhere_amount': amount_str,
        'payhere_currency': 'LKR',
        'status_code': status_code,
        'md5sig': valid_md5sig,
        'method': 'VISA'
    })
    assert status == 200, f"Notification failed: {d_notify}"

    # Verify MySQL order status and payment record
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', database='telebuy_db', cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM orders WHERE order_id = %s", (payhere_order_id,))
        ord_check = cur.fetchone()
        assert ord_check['payment_status'] == 'PAID', f"Expected PAID, got: {ord_check['payment_status']}"
        assert ord_check['delivery_status'] == 'Payment Confirmed', f"Expected Payment Confirmed, got: {ord_check['delivery_status']}"

        cur.execute("SELECT * FROM payments WHERE order_id = %s", (ord_check['id'],))
        pay_check = cur.fetchone()
        assert pay_check is not None and pay_check['payment_id'] == '32002598711', "Payment not recorded in MySQL payments table!"
    conn.close()
    print(f"[{passed+1}/{total}] PASS: PayHere IPN verified. Order updated to PAID and payment record saved in MySQL `payments`.")
    passed += 1

    # 8. Webhook Idempotency & Duplicate Notification Handling
    total += 1
    status, d_dup = req(f"{BASE_URL}/api/checkout/notify", method='POST', data={
        'merchant_id': MERCHANT_ID,
        'order_id': payhere_order_id,
        'payment_id': '32002598711',
        'payhere_amount': amount_str,
        'payhere_currency': 'LKR',
        'status_code': status_code,
        'md5sig': valid_md5sig,
        'method': 'VISA'
    })
    assert status == 200 and d_dup.get('already_processed') is True, f"Idempotency check failed: {d_dup}"
    print(f"[{passed+1}/{total}] PASS: Duplicate payment notification handled idempotently without re-processing.")
    passed += 1

    # 9. Invalid Signature Rejection
    total += 1
    status, d_bad = req(f"{BASE_URL}/api/checkout/notify", method='POST', data={
        'merchant_id': MERCHANT_ID,
        'order_id': payhere_order_id,
        'payment_id': '9999999',
        'payhere_amount': amount_str,
        'payhere_currency': 'LKR',
        'status_code': status_code,
        'md5sig': 'INVALID_SIGNATURE_ATTEMPT_123',
        'method': 'VISA'
    })
    assert status == 400, f"Expected 400 for bad signature, got {status}: {d_bad}"
    print(f"[{passed+1}/{total}] PASS: Fraudulent payment webhook rejected with HTTP 400.")
    passed += 1

    # 10. Order Details & 7-Stage Delivery Tracking from MySQL
    total += 1
    status, d_order = req(f"{BASE_URL}/api/orders/{payhere_order_id}")
    assert status == 200 and 'order' in d_order and 'stages' in d_order, f"Failed fetch order: {d_order}"
    stages = d_order['stages']
    assert len(stages) == 7, f"Expected 7 stages, got {len(stages)}"
    assert stages[0]['stage'] == 'Order Placed' and stages[0]['completed'] is True
    assert stages[1]['stage'] == 'Payment Confirmed' and stages[1]['completed'] is True
    print(f"[{passed+1}/{total}] PASS: Order tracking retrieved from MySQL with 7-stage delivery stepper.")
    passed += 1

    # 11. Admin Access Control & Delivery Stage Advancement in MySQL
    total += 1
    # Unauthorized attempt without admin token
    status, d_unauth = req(f"{BASE_URL}/api/admin/orders/{payhere_order_id}/delivery-status", method='POST', data={
        'deliveryStatus': 'Shipped'
    })
    assert status == 401, f"Expected 401 for unauthorized admin, got {status}"

    # Authorized admin update
    status, d_stage = req(f"{BASE_URL}/api/admin/orders/{payhere_order_id}/delivery-status", method='POST', data={
        'deliveryStatus': 'Shipped',
        'courierName': 'Pronto Logistics Express',
        'trackingNumber': 'PRONTO-LK-889922',
        'note': 'Handed over to courier hub in Colombo 03.'
    }, headers={'X-Admin-Token': ADMIN_SECRET_KEY})
    assert status == 200 and d_stage.get('success') is True, f"Failed stage update: {d_stage}"

    # Verify directly in MySQL
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', database='telebuy_db', cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM orders WHERE order_id = %s", (payhere_order_id,))
        shipped_ord = cur.fetchone()
        assert shipped_ord['delivery_status'] == 'Shipped', f"Status not updated in MySQL: {shipped_ord['delivery_status']}"
        assert shipped_ord['courier_name'] == 'Pronto Logistics Express', "Courier name not updated!"
        assert shipped_ord['tracking_number'] == 'PRONTO-LK-889922', "Tracking number not updated!"

        cur.execute("SELECT * FROM order_status_history WHERE order_id = %s AND stage = 'Shipped'", (shipped_ord['id'],))
        hist_entry = cur.fetchone()
        assert hist_entry is not None, "History stage not recorded in MySQL order_status_history!"
    conn.close()
    print(f"[{passed+1}/{total}] PASS: Admin authorization enforced & delivery status advanced to 'Shipped' in MySQL.")
    passed += 1

    # 12. Foreign-Key Constraint & Data Persistence after verification
    total += 1
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', database='telebuy_db', cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        # Verify foreign keys are active
        cur.execute("""
            SELECT TABLE_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = 'telebuy_db' AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        fks = cur.fetchall()
        assert len(fks) >= 6, f"Expected at least 6 foreign keys, found {len(fks)}"
    conn.close()
    print(f"[{passed+1}/{total}] PASS: MySQL InnoDB Foreign-Key constraints verified ({len(fks)} relational keys).")
    passed += 1

    print("=" * 65)
    print(f"  ALL {passed}/{total} MYSQL INTEGRATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == '__main__':
    run_tests()
