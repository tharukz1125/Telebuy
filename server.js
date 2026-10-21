/**
 * TeleBuy.lk — Backend Server & PayHere Payment Gateway Integration
 * 
 * Features:
 * 1. Secure Environment Variable Management (.env for Merchant Secret)
 * 2. Server-side Cart Price Validation against Authoritative Catalog
 * 3. Unique Order ID Generation
 * 4. Dual Payment Support: PayHere Online Gateway & Cash on Delivery (COD)
 * 5. Official 7-Stage Delivery Status Tracking & Real Timelines
 * 6. Admin Order Management & Delivery Update API
 * 7. Webhook/IPN Payment Notification Verification with Idempotency
 * 8. Static Asset & Webpage Serving
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const crypto = require('crypto');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const BASE_URL = process.env.BASE_URL || `http://localhost:${PORT}`;
const MERCHANT_ID = process.env.MERCHANT_ID || '1238371';
const MERCHANT_SECRET = process.env.MERCHANT_SECRET || 'NDE2Njk4MTMzNzE3ODQzNjI3NjMzNzQ0NjI1MTAyMzgwNTM1MzgwNA==';
const ADMIN_SECRET_KEY = process.env.ADMIN_SECRET_KEY || 'telebuy_admin_secret_2026';
const PAYHERE_MODE = (process.env.PAYHERE_MODE || 'sandbox').toLowerCase();

const PAYHERE_ACTION_URL = PAYHERE_MODE === 'live'
  ? 'https://www.payhere.lk/pay/checkout'
  : 'https://sandbox.payhere.lk/pay/checkout';

// 7 Official Delivery Stages (as requested in Requirement 4)
const VALID_DELIVERY_STAGES = [
  "Order Placed",
  "Payment Confirmed",
  "Processing",
  "Packed",
  "Shipped",
  "Out for Delivery",
  "Delivered"
];

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static frontend files (HTML, CSS, JS, Assets)
app.use(express.static(path.join(__dirname)));

// ============================================================
// AUTHORITATIVE PRODUCT CATALOG (Server-side Price Truth)
// ============================================================
const SERVER_CATALOG = {
  // Home Page Featured
  "feat-1": { title: "Samsung 55\" QLED 4K Smart TV", priceNum: 289900, brand: "Samsung", image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80" },
  "feat-2": { title: "LG 55\" OLED Smart TV", priceNum: 524900, brand: "LG", image: "https://images.unsplash.com/photo-1717295248302-543d5a49091f?auto=format&fit=crop&w=800&q=80" },
  "feat-3": { title: "Sony 43\" LED Full HD TV", priceNum: 134900, brand: "Sony", image: "https://images.unsplash.com/photo-1461151304267-38535e780c79?auto=format&fit=crop&w=800&q=85" },
  "feat-4": { title: "TCL 65\" 8K Smart TV", priceNum: 412900, brand: "TCL", image: "https://images.unsplash.com/photo-1521607630287-ee2e81ad3ced?auto=format&fit=crop&w=800&q=80" },

  // QLED TVs
  "qled-1": { title: "Samsung 65\" Neo QLED 4K Smart TV (QN90C)", priceNum: 439900, brand: "Samsung", image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80" },
  "qled-2": { title: "Sony Bravia XR 55\" Full Array QLED TV (XR-55X90L)", priceNum: 385000, brand: "Sony", image: "https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80" },
  "qled-3": { title: "TCL 75\" C845 Mini-LED QLED 144Hz Game Master TV", priceNum: 499900, brand: "TCL", image: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80" },
  "qled-4": { title: "Hisense 65\" U8K Quantum Dot ULED Mini-LED TV", priceNum: 329900, brand: "Hisense", image: "https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=800&q=80" },
  "qled-5": { title: "LG 55\" QNED85 Mini-LED Quantum Dot 4K TV", priceNum: 365000, brand: "LG", image: "https://images.unsplash.com/photo-1552975084-6e027cd345c2?auto=format&fit=crop&w=800&q=80" },

  // OLED TVs
  "oled-1": { title: "LG 65\" OLED evo C3 Series 4K Cinema TV", priceNum: 549900, brand: "LG", image: "https://images.unsplash.com/photo-1717295248302-543d5a49091f?auto=format&fit=crop&w=800&q=80" },
  "oled-2": { title: "Sony Bravia XR 55\" A80L OLED Master Series TV", priceNum: 515000, brand: "Sony", image: "https://images.unsplash.com/photo-1717295248230-93ea71f48f92?auto=format&fit=crop&w=800&q=80" },
  "oled-3": { title: "Samsung 65\" S95C Quantum OLED 4K Flagship TV", priceNum: 629900, brand: "Samsung", image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80" },
  "oled-4": { title: "Panasonic 55\" MZ2000 Master OLED Pro Cinema TV", priceNum: 489900, brand: "Panasonic", image: "https://images.unsplash.com/photo-1521607630287-ee2e81ad3ced?auto=format&fit=crop&w=800&q=80" },
  "oled-5": { title: "LG 77\" OLED evo G3 Gallery Edition 4K TV", priceNum: 985000, brand: "LG", image: "https://images.unsplash.com/photo-1730909352933-614f1673ac21?auto=format&fit=crop&w=800&q=80" },

  // 8K TVs
  "8k-1": { title: "Samsung 75\" Neo QLED 8K TV (QN900C)", priceNum: 1450000, brand: "Samsung", image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80" },
  "8k-2": { title: "Sony Bravia XR 75\" Z9K Master Series 8K Mini-LED", priceNum: 1890000, brand: "Sony", image: "https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80" },
  "8k-3": { title: "LG 77\" Signature OLED 8K TV (Z3 Series)", priceNum: 2650000, brand: "LG", image: "https://images.unsplash.com/photo-1717295248302-543d5a49091f?auto=format&fit=crop&w=800&q=80" },
  "8k-4": { title: "TCL 65\" 8K Mini-LED Quantum TV (X925 Pro)", priceNum: 680000, brand: "TCL", image: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80" },
  "8k-5": { title: "Samsung 65\" Neo QLED 8K TV (QN800C)", priceNum: 890000, brand: "Samsung", image: "https://images.unsplash.com/photo-1521607630287-ee2e81ad3ced?auto=format&fit=crop&w=800&q=80" },

  // Smart TVs
  "smart-1": { title: "Samsung 55\" Crystal UHD 4K Smart TV (CU8000)", priceNum: 219900, brand: "Samsung", image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80" },
  "smart-2": { title: "Sony Bravia 50\" 4K Google TV (KD-50X77L)", priceNum: 249000, brand: "Sony", image: "https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80" },
  "smart-3": { title: "LG 55\" 4K UHD Smart TV (UR80 Series)", priceNum: 235000, brand: "LG", image: "https://images.unsplash.com/photo-1552975084-6e027cd345c2?auto=format&fit=crop&w=800&q=80" },
  "smart-4": { title: "TCL 50\" P745 4K Google Smart TV", priceNum: 169900, brand: "TCL", image: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80" },
  "smart-5": { title: "Xiaomi 55\" 4K Google TV (A Pro Series)", priceNum: 159900, brand: "Xiaomi", image: "https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=800&q=80" },

  // LED TVs
  "led-1": { title: "Samsung 43\" Full HD Smart LED TV (T5300)", priceNum: 119900, brand: "Samsung", image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80" },
  "led-2": { title: "Sony Bravia 43\" Full HD LED TV (W6600)", priceNum: 138000, brand: "Sony", image: "https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80" },
  "led-3": { title: "LG 43\" Full HD Smart LED TV (LM5750 Series)", priceNum: 125000, brand: "LG", image: "https://images.unsplash.com/photo-1552975084-6e027cd345c2?auto=format&fit=crop&w=800&q=80" },
  "led-4": { title: "TCL 40\" Full HD Google Smart LED TV (S5400)", priceNum: 89900, brand: "TCL", image: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80" },
  "led-5": { title: "Hisense 32\" HD Smart LED TV (A4K Series)", priceNum: 54900, brand: "Hisense", image: "https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=800&q=80" },

  // Accessories
  "acc-1": { title: "Samsung 3.1.2ch Dolby Atmos Soundbar (HW-Q600C)", priceNum: 89900, brand: "Samsung", image: "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80" },
  "acc-2": { title: "Sony HT-S20R 5.1ch Surround Soundbar System (400W)", priceNum: 68000, brand: "Sony", image: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80" },
  "acc-3": { title: "North Bayou NB-P6 Full Motion Cantilever Wall Mount (45\"-75\")", priceNum: 14500, brand: "North Bayou", image: "https://images.unsplash.com/photo-1584905066893-7d5c142ba4e1?auto=format&fit=crop&w=800&q=80" },
  "acc-4": { title: "Baseus 8K Ultra High Speed HDMI 2.1 Cable (3m, 48Gbps)", priceNum: 4900, brand: "Baseus", image: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80" },
  "acc-5": { title: "Universal Voice Air-Mouse Remote with Backlit Keyboard", priceNum: 3500, brand: "TeleBuy", image: "https://images.unsplash.com/photo-1735212769704-d03b95dd1a14?auto=format&fit=crop&w=800&q=80" }
};

// In-Memory Order Storage (keyed by order_id)
const ORDERS_DB = new Map();

function generatePayHereHash(merchantId, orderId, formattedAmount, currency, merchantSecret) {
  const hashedSecret = crypto
    .createHash('md5')
    .update(merchantSecret)
    .digest('hex')
    .toUpperCase();

  const hashString = `${merchantId}${orderId}${formattedAmount}${currency}${hashedSecret}`;

  return crypto
    .createHash('md5')
    .update(hashString)
    .digest('hex')
    .toUpperCase();
}

function calculateEstimatedDelivery(daysOffset = 3) {
  const d = new Date();
  d.setDate(d.getDate() + daysOffset);
  return d.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
}

function checkAdminAuth(req) {
  const token = req.headers['x-admin-token'] || (req.headers.authorization && req.headers.authorization.replace('Bearer ', ''));
  return token === ADMIN_SECRET_KEY;
}

function formatOrderRecord(order) {
  const currentStage = order.delivery_status || order.deliveryStatus || "Order Placed";
  const currentStageIdx = VALID_DELIVERY_STAGES.indexOf(currentStage);

  const historyMap = new Map();
  (order.delivery_history || []).forEach(h => historyMap.set(h.stage, h));

  const tracking_stages = VALID_DELIVERY_STAGES.map((stageName, idx) => {
    const hist = historyMap.get(stageName);
    const completed = idx < currentStageIdx || (stageName === currentStage && currentStage === "Delivered");
    const current = (stageName === currentStage && currentStage !== "Delivered") || (stageName === "Delivered" && currentStage === "Delivered");

    return {
      stage: stageName,
      index: idx + 1,
      completed: Boolean(completed || hist),
      current: current,
      timestamp: hist ? hist.timestamp : null,
      description: hist ? hist.description : null,
      updated_by: hist ? hist.updated_by : null
    };
  });

  return {
    ...order,
    id: order.order_id || order.orderId,
    orderId: order.order_id || order.orderId,
    amount: order.total_amount || order.amount,
    paymentStatus: order.payment_status || order.paymentStatus,
    orderStatus: order.order_status || order.orderStatus,
    deliveryStatus: currentStage,
    tracking_stages
  };
}

// ============================================================
// API 1: INITIATE PAYMENT (PayHere OR Cash on Delivery)
// POST /api/checkout/initiate-payment
// ============================================================
app.post('/api/checkout/initiate-payment', (req, res) => {
  try {
    const { items, customer, paymentMethod = 'payhere', customerId } = req.body;

    if (!items || !Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ success: false, message: 'Your shopping cart is empty.' });
    }

    const customerFirstName = (customer.firstName || customer.first_name || '').trim();
    const customerLastName = (customer.lastName || customer.last_name || '').trim();
    const customerEmail = (customer.email || '').trim().toLowerCase();
    const customerPhone = (customer.phone || '').trim();
    const customerAddress = (customer.address || '').trim();
    const customerCity = (customer.city || '').trim();
    const customerPostalCode = (customer.postalCode || customer.postal_code || '00300').trim();

    if (!customer || !customerFirstName || !customerEmail || !customerPhone || !customerAddress || !customerCity) {
      return res.status(400).json({ success: false, message: 'Please provide all required delivery and contact details.' });
    }

    const cleanPaymentMethod = paymentMethod.toLowerCase().trim();
    if (!['payhere', 'cod'].includes(cleanPaymentMethod)) {
      return res.status(400).json({ success: false, message: 'Invalid payment method selected.' });
    }

    // 1. Price Verification
    let subtotal = 0;
    const verifiedItems = [];
    const itemNames = [];

    for (const item of items) {
      const product = SERVER_CATALOG[item.id];
      if (!product) {
        return res.status(400).json({ success: false, message: `Product "${item.id}" is no longer available.` });
      }
      const qty = Math.max(1, parseInt(item.qty || item.quantity, 10) || 1);
      const lineTotal = product.priceNum * qty;
      subtotal += lineTotal;

      verifiedItems.push({
        id: item.id,
        product_id: item.id,
        title: product.title,
        brand: product.brand,
        image: product.image,
        unitPrice: product.priceNum,
        qty: qty,
        lineTotal: lineTotal
      });

      itemNames.push(`${product.title} (x${qty})`);
    }

    const deliveryFee = 0;
    const finalAmount = subtotal + deliveryFee;
    const formattedAmount = Number(finalAmount).toFixed(2);
    const currency = 'LKR';

    const randomSuffix = Math.floor(10000 + Math.random() * 90000);
    const orderId = `TB-${new Date().getFullYear()}-${randomSuffix}`;
    const nowIso = new Date().toISOString();
    const estDelivery = calculateEstimatedDelivery(3);

    const isCod = cleanPaymentMethod === 'cod';
    const payStatus = isCod ? 'PENDING_COD' : 'PENDING';
    const ordStatus = isCod ? 'Order Confirmed' : 'Pending Payment';
    const delivStatus = isCod ? 'Payment Confirmed' : 'Order Placed';

    const history = [
      {
        stage: 'Order Placed',
        description: isCod ? 'Customer placed order using Cash on Delivery (COD).' : 'Customer initialized PayHere online checkout session.',
        updated_by: 'System',
        timestamp: nowIso
      }
    ];

    if (isCod) {
      history.push({
        stage: 'Payment Confirmed',
        description: 'Cash on Delivery terms accepted. Payment will be collected upon delivery.',
        updated_by: 'System',
        timestamp: nowIso
      });
    }

    const orderRecord = {
      orderId,
      order_id: orderId,
      customerId: customerId || null,
      customer_id: customerId || null,
      customer_name: `${customer.firstName} ${customer.lastName || ''}`.trim(),
      customer_email: customer.email.trim().toLowerCase(),
      customer_phone: customer.phone.trim(),
      customer: {
        firstName: customer.firstName.trim(),
        lastName: (customer.lastName || '').trim(),
        email: customer.email.trim().toLowerCase(),
        phone: customer.phone.trim(),
        address: customer.address.trim(),
        city: customer.city.trim(),
        postalCode: (customer.postalCode || '00300').trim(),
        country: 'Sri Lanka',
        notes: (customer.notes || customer.deliveryNotes || '').trim()
      },
      shipping_address: {
        street: customer.address.trim(),
        city: customer.city.trim(),
        postalCode: (customer.postalCode || '00300').trim(),
        country: 'Sri Lanka'
      },
      items: verifiedItems,
      subtotal,
      delivery_fee: deliveryFee,
      total_amount: finalAmount,
      amount: finalAmount,
      formattedAmount,
      currency,
      payment_method: cleanPaymentMethod,
      paymentMethod: cleanPaymentMethod,
      payment_status: payStatus,
      paymentStatus: payStatus,
      order_status: ordStatus,
      orderStatus: ordStatus,
      delivery_status: delivStatus,
      deliveryStatus: delivStatus,
      estimated_delivery: estDelivery,
      estimatedDelivery: estDelivery,
      delivery_history: history,
      created_at: nowIso,
      updated_at: nowIso
    };

    ORDERS_DB.set(orderId, orderRecord);

    if (isCod) {
      return res.status(200).json({
        success: true,
        orderId,
        paymentMethod: 'cod',
        message: 'Order placed successfully with Cash on Delivery.',
        redirectUrl: `order-confirmation.html?order_id=${orderId}&status=cod_success`
      });
    }

    // PayHere Online
    const hash = generatePayHereHash(MERCHANT_ID, orderId, formattedAmount, currency, MERCHANT_SECRET);

    const payherePayload = {
      merchant_id: MERCHANT_ID,
      return_url: `${BASE_URL}/order-confirmation.html?status=success&order_id=${orderId}`,
      cancel_url: `${BASE_URL}/order-confirmation.html?status=cancelled&order_id=${orderId}`,
      notify_url: `${BASE_URL}/api/checkout/notify`,
      order_id: orderId,
      items: itemNames.join(', ').substring(0, 255),
      currency: currency,
      amount: formattedAmount,
      first_name: customer.firstName.trim(),
      last_name: (customer.lastName || '').trim(),
      email: customer.email.trim().toLowerCase(),
      phone: customer.phone.trim(),
      address: customer.address.trim(),
      city: customer.city.trim(),
      country: 'Sri Lanka',
      hash: hash
    };

    res.status(200).json({
      success: true,
      orderId,
      paymentMethod: 'payhere',
      paymentUrl: PAYHERE_ACTION_URL,
      actionUrl: PAYHERE_ACTION_URL,
      params: payherePayload,
      payhereData: payherePayload
    });

  } catch (err) {
    console.error('[TeleBuy Server] Checkout initiation error:', err);
    res.status(500).json({ success: false, message: 'Internal server error occurred.' });
  }
});

// ============================================================
// API 2: RETRY PAYMENT FOR EXISTING PENDING/CANCELLED/FAILED ORDER
// POST /api/orders/:orderId/retry-payment
// ============================================================
app.post('/api/orders/:orderId/retry-payment', (req, res) => {
  const { orderId } = req.params;
  const order = ORDERS_DB.get(orderId);

  if (!order) {
    return res.status(404).json({ success: false, message: 'Order not found.' });
  }

  if (order.payment_status === 'PAID') {
    return res.status(400).json({ success: false, message: 'This order has already been verified and paid.' });
  }

  const hash = generatePayHereHash(MERCHANT_ID, orderId, order.formattedAmount, order.currency, MERCHANT_SECRET);

  const payherePayload = {
    merchant_id: MERCHANT_ID,
    return_url: `${BASE_URL}/order-confirmation.html?status=success&order_id=${orderId}`,
    cancel_url: `${BASE_URL}/order-confirmation.html?status=cancelled&order_id=${orderId}`,
    notify_url: `${BASE_URL}/api/checkout/notify`,
    order_id: orderId,
    items: order.items.map(it => `${it.title} (x${it.qty})`).join(', ').substring(0, 255),
    currency: order.currency,
    amount: order.formattedAmount,
    first_name: order.customer.firstName,
    last_name: order.customer.lastName,
    email: order.customer.email,
    phone: order.customer.phone,
    address: order.customer.address,
    city: order.customer.city,
    country: 'Sri Lanka',
    hash: hash
  };

  res.status(200).json({
    success: true,
    orderId,
    paymentUrl: PAYHERE_ACTION_URL,
    actionUrl: PAYHERE_ACTION_URL,
    params: payherePayload,
    payhereData: payherePayload
  });
});

// ============================================================
// API 3: PAYHERE IPN WEBHOOK
// POST /api/checkout/notify
// ============================================================
app.post('/api/checkout/notify', (req, res) => {
  try {
    const {
      merchant_id,
      order_id,
      payment_id,
      payhere_amount,
      payhere_currency,
      status_code,
      md5sig
    } = req.body;

    const hashedSecret = crypto
      .createHash('md5')
      .update(MERCHANT_SECRET)
      .digest('hex')
      .toUpperCase();

    const expectedSig = crypto
      .createHash('md5')
      .update(`${merchant_id}${order_id}${payhere_amount}${payhere_currency}${status_code}${hashedSecret}`)
      .digest('hex')
      .toUpperCase();

    if (expectedSig !== md5sig) {
      console.warn(`[TeleBuy IPN] Signature mismatch for Order ${order_id}! Rejecting webhook.`);
      return res.status(400).send('Signature Verification Failed');
    }

    const order = ORDERS_DB.get(order_id);
    if (!order) {
      return res.status(404).send('Order Not Found');
    }

    if (order.payment_status === 'PAID' && status_code === '2') {
      return res.status(200).send('OK (Already processed)');
    }

    const nowIso = new Date().toISOString();
    order.updated_at = nowIso;

    if (status_code === '2') {
      order.payment_status = 'PAID';
      order.paymentStatus = 'PAID';
      order.order_status = 'Order Confirmed';
      order.orderStatus = 'Order Confirmed';
      if (order.delivery_status === 'Order Placed') {
        order.delivery_status = 'Payment Confirmed';
        order.deliveryStatus = 'Payment Confirmed';
      }
      order.payhere_payment_id = payment_id;
      order.delivery_history.push({
        stage: 'Payment Confirmed',
        description: `PayHere payment verified successfully. Transaction Ref: ${payment_id || 'N/A'}`,
        updated_by: 'PayHere Gateway',
        timestamp: nowIso
      });
    } else if (status_code === '-1') {
      order.payment_status = 'CANCELLED';
      order.paymentStatus = 'CANCELLED';
    } else if (status_code === '-2') {
      order.payment_status = 'FAILED';
      order.paymentStatus = 'FAILED';
    }

    ORDERS_DB.set(order_id, order);
    res.status(200).send('OK');
  } catch (err) {
    console.error('[TeleBuy IPN] Webhook processing error:', err);
    res.status(500).send('Error');
  }
});

// ============================================================
// API 4: GET SINGLE ORDER DETAILS
// GET /api/orders/:orderId
// ============================================================
app.get('/api/orders/:orderId', (req, res) => {
  const { orderId } = req.params;
  const order = ORDERS_DB.get(orderId);

  if (!order) {
    return res.status(404).json({ success: false, message: 'Order not found.' });
  }

  res.status(200).json({ success: true, order: formatOrderRecord(order) });
});

// ============================================================
// API 5: CUSTOMER ORDER HISTORY
// GET /api/customer/orders?email=...&customerId=...
// ============================================================
app.get('/api/customer/orders', (req, res) => {
  const email = (req.query.email || '').trim().toLowerCase();
  const customerId = (req.query.customerId || '').trim();

  if (!email && !customerId) {
    return res.status(400).json({ success: false, message: 'Please provide customer email or account ID.' });
  }

  const results = [];
  ORDERS_DB.forEach(ord => {
    if ((customerId && (ord.customerId === customerId || ord.customer_id === customerId)) ||
        (email && ord.customer_email === email)) {
      results.push(formatOrderRecord(ord));
    }
  });

  results.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  res.status(200).json({ success: true, orders: results, count: results.length });
});

// ============================================================
// API 6: ADMIN ORDER LIST
// GET /api/admin/orders
// ============================================================
app.get('/api/admin/orders', (req, res) => {
  if (!checkAdminAuth(req)) {
    return res.status(401).json({ success: false, message: 'Unauthorized admin access.' });
  }

  const { status, search } = req.query;
  const list = [];

  ORDERS_DB.forEach(ord => {
    const formatted = formatOrderRecord(ord);
    let match = true;

    if (status && status.toLowerCase() !== 'all' && formatted.paymentStatus !== status && formatted.deliveryStatus !== status) {
      match = false;
    }

    if (search) {
      const q = search.toLowerCase();
      const combined = `${formatted.orderId} ${formatted.customer_name} ${formatted.customer_email} ${formatted.customer_phone} ${formatted.tracking_number || ''}`.toLowerCase();
      if (!combined.includes(q)) match = false;
    }

    if (match) list.push(formatted);
  });

  list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  res.status(200).json({ success: true, orders: list, total: list.length });
});

// ============================================================
// API 7: ADMIN UPDATE DELIVERY STATUS
// POST /api/admin/orders/:orderId/delivery-status
// ============================================================
app.post('/api/admin/orders/:orderId/delivery-status', (req, res) => {
  if (!checkAdminAuth(req)) {
    return res.status(401).json({ success: false, message: 'Unauthorized admin request.' });
  }

  const { orderId } = req.params;
  const order = ORDERS_DB.get(orderId);
  if (!order) {
    return res.status(404).json({ success: false, message: 'Order not found.' });
  }

  const deliveryStatus = req.body.deliveryStatus || req.body.delivery_status || req.body.stage;
  const trackingNumber = req.body.trackingNumber || req.body.tracking_number;
  const courierName = req.body.courierName || req.body.courier_name;
  const note = req.body.note || req.body.notes || req.body.description;
  if (!VALID_DELIVERY_STAGES.includes(deliveryStatus)) {
    return res.status(400).json({ success: false, message: `Invalid delivery stage. Must be one of: ${VALID_DELIVERY_STAGES.join(', ')}` });
  }

  const nowIso = new Date().toISOString();
  order.delivery_status = deliveryStatus;
  order.deliveryStatus = deliveryStatus;
  if (trackingNumber) order.tracking_number = trackingNumber;
  if (courierName) order.courier_name = courierName;
  order.updated_at = nowIso;

  order.delivery_history.push({
    stage: deliveryStatus,
    description: note || `Status updated to '${deliveryStatus}' by Administrator`,
    updated_by: 'Administrator',
    timestamp: nowIso
  });

  ORDERS_DB.set(orderId, order);
  res.status(200).json({
    success: true,
    message: `Order ${orderId} delivery status updated to '${deliveryStatus}'.`,
    order: formatOrderRecord(order)
  });
});

// Health Endpoint
app.get('/api/health', (req, res) => {
  res.status(200).json({
    status: 'ONLINE',
    store: 'TeleBuy.lk',
    gateway: 'PayHere',
    mode: PAYHERE_MODE,
    merchantIdConfigured: Boolean(MERCHANT_ID)
  });
});

app.listen(PORT, () => {
  console.log(`=======================================================`);
  console.log(`🚀 TeleBuy.lk Server running at http://localhost:${PORT}`);
  console.log(`💳 PayHere Gateway Mode: [${PAYHERE_MODE.toUpperCase()}]`);
  console.log(`🔒 Merchant Secret & Admin API: Protected`);
  console.log(`=======================================================`);
});
