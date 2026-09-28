/**
 * TeleBuy.lk — Central Store & Persistence Engine (Cart & Wishlist)
 * Vanilla JavaScript utilizing localStorage for state persistence across all pages.
 */

// Global Product Catalog
const TELEBUY_CATALOG = {
  // Home Page Featured
  "feat-1": {
    id: "feat-1",
    brand: "Samsung",
    title: "Samsung 55\" QLED 4K Smart TV",
    price: "Rs. 289,900",
    priceNum: 289900,
    image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80",
    category: "QLED TVs"
  },
  "feat-2": {
    id: "feat-2",
    brand: "LG",
    title: "LG 55\" OLED Smart TV",
    price: "Rs. 524,900",
    priceNum: 524900,
    image: "https://images.unsplash.com/photo-1717295248302-543d5a49091f?auto=format&fit=crop&w=800&q=80",
    category: "OLED TVs"
  },
  "feat-3": {
    id: "feat-3",
    brand: "Sony",
    title: "Sony 43\" LED Full HD TV",
    price: "Rs. 134,900",
    priceNum: 134900,
    image: "https://images.unsplash.com/photo-1461151304267-38535e780c79?auto=format&fit=crop&w=800&q=85",
    category: "LED TVs"
  },
  "feat-4": {
    id: "feat-4",
    brand: "TCL",
    title: "TCL 65\" 8K Smart TV",
    price: "Rs. 412,900",
    priceNum: 412900,
    image: "https://images.unsplash.com/photo-1521607630287-ee2e81ad3ced?auto=format&fit=crop&w=800&q=80",
    category: "8K TVs"
  },

  // QLED TVs
  "qled-1": {
    id: "qled-1",
    brand: "Samsung",
    title: "Samsung 65\" Neo QLED 4K Smart TV (QN90C)",
    price: "Rs. 439,900",
    priceNum: 439900,
    image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80",
    category: "QLED TVs"
  },
  "qled-2": {
    id: "qled-2",
    brand: "Sony",
    title: "Sony Bravia XR 55\" Full Array QLED TV (XR-55X90L)",
    price: "Rs. 385,000",
    priceNum: 385000,
    image: "https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80",
    category: "QLED TVs"
  },
  "qled-3": {
    id: "qled-3",
    brand: "TCL",
    title: "TCL 75\" C845 Mini-LED QLED 144Hz Game Master TV",
    price: "Rs. 499,900",
    priceNum: 499900,
    image: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80",
    category: "QLED TVs"
  },
  "qled-4": {
    id: "qled-4",
    brand: "Hisense",
    title: "Hisense 65\" U8K Quantum Dot ULED Mini-LED TV",
    price: "Rs. 329,900",
    priceNum: 329900,
    image: "https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=800&q=80",
    category: "QLED TVs"
  },
  "qled-5": {
    id: "qled-5",
    brand: "LG",
    title: "LG 55\" QNED85 Mini-LED Quantum Dot 4K TV",
    price: "Rs. 365,000",
    priceNum: 365000,
    image: "https://images.unsplash.com/photo-1552975084-6e027cd345c2?auto=format&fit=crop&w=800&q=80",
    category: "QLED TVs"
  },

  // OLED TVs
  "oled-1": {
    id: "oled-1",
    brand: "LG",
    title: "LG 65\" OLED evo C3 Series 4K Cinema TV",
    price: "Rs. 549,900",
    priceNum: 549900,
    image: "https://images.unsplash.com/photo-1717295248302-543d5a49091f?auto=format&fit=crop&w=800&q=80",
    category: "OLED TVs"
  },
  "oled-2": {
    id: "oled-2",
    brand: "Sony",
    title: "Sony Bravia XR 55\" A80L OLED Master Series TV",
    price: "Rs. 515,000",
    priceNum: 515000,
    image: "https://images.unsplash.com/photo-1717295248230-93ea71f48f92?auto=format&fit=crop&w=800&q=80",
    category: "OLED TVs"
  },
  "oled-3": {
    id: "oled-3",
    brand: "Samsung",
    title: "Samsung 65\" S95C Quantum OLED 4K Flagship TV",
    price: "Rs. 629,900",
    priceNum: 629900,
    image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80",
    category: "OLED TVs"
  },
  "oled-4": {
    id: "oled-4",
    brand: "Panasonic",
    title: "Panasonic 55\" MZ2000 Master OLED Pro Cinema TV",
    price: "Rs. 489,900",
    priceNum: 489900,
    image: "https://images.unsplash.com/photo-1521607630287-ee2e81ad3ced?auto=format&fit=crop&w=800&q=80",
    category: "OLED TVs"
  },
  "oled-5": {
    id: "oled-5",
    brand: "LG",
    title: "LG 77\" OLED evo G3 Gallery Edition 4K TV",
    price: "Rs. 985,000",
    priceNum: 985000,
    image: "https://images.unsplash.com/photo-1730909352933-614f1673ac21?auto=format&fit=crop&w=800&q=80",
    category: "OLED TVs"
  },

  // 8K TVs
  "8k-1": {
    id: "8k-1",
    brand: "Samsung",
    title: "Samsung 75\" Neo QLED 8K TV (QN900C)",
    price: "Rs. 1,450,000",
    priceNum: 1450000,
    image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80",
    category: "8K TVs"
  },
  "8k-2": {
    id: "8k-2",
    brand: "Sony",
    title: "Sony Bravia XR 75\" Z9K Master Series 8K Mini-LED",
    price: "Rs. 1,890,000",
    priceNum: 1890000,
    image: "https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80",
    category: "8K TVs"
  },
  "8k-3": {
    id: "8k-3",
    brand: "LG",
    title: "LG 77\" Signature OLED 8K TV (Z3 Series)",
    price: "Rs. 2,650,000",
    priceNum: 2650000,
    image: "https://images.unsplash.com/photo-1717295248302-543d5a49091f?auto=format&fit=crop&w=800&q=80",
    category: "8K TVs"
  },
  "8k-4": {
    id: "8k-4",
    brand: "TCL",
    title: "TCL 65\" 8K Mini-LED Quantum TV (X925 Pro)",
    price: "Rs. 680,000",
    priceNum: 680000,
    image: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80",
    category: "8K TVs"
  },
  "8k-5": {
    id: "8k-5",
    brand: "Samsung",
    title: "Samsung 65\" Neo QLED 8K TV (QN800C)",
    price: "Rs. 890,000",
    priceNum: 890000,
    image: "https://images.unsplash.com/photo-1521607630287-ee2e81ad3ced?auto=format&fit=crop&w=800&q=80",
    category: "8K TVs"
  },

  // Smart TVs
  "smart-1": {
    id: "smart-1",
    brand: "Samsung",
    title: "Samsung 55\" Crystal UHD 4K Smart TV (CU8000)",
    price: "Rs. 219,900",
    priceNum: 219900,
    image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80",
    category: "Smart TVs"
  },
  "smart-2": {
    id: "smart-2",
    brand: "Sony",
    title: "Sony Bravia 50\" 4K Google TV (KD-50X77L)",
    price: "Rs. 249,000",
    priceNum: 249000,
    image: "https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80",
    category: "Smart TVs"
  },
  "smart-3": {
    id: "smart-3",
    brand: "LG",
    title: "LG 55\" 4K UHD Smart TV (UR80 Series)",
    price: "Rs. 235,000",
    priceNum: 235000,
    image: "https://images.unsplash.com/photo-1552975084-6e027cd345c2?auto=format&fit=crop&w=800&q=80",
    category: "Smart TVs"
  },
  "smart-4": {
    id: "smart-4",
    brand: "TCL",
    title: "TCL 50\" P745 4K Google Smart TV",
    price: "Rs. 169,900",
    priceNum: 169900,
    image: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80",
    category: "Smart TVs"
  },
  "smart-5": {
    id: "smart-5",
    brand: "Xiaomi",
    title: "Xiaomi 55\" 4K Google TV (A Pro Series)",
    price: "Rs. 159,900",
    priceNum: 159900,
    image: "https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=800&q=80",
    category: "Smart TVs"
  },

  // LED TVs
  "led-1": {
    id: "led-1",
    brand: "Samsung",
    title: "Samsung 43\" Full HD Smart LED TV (T5300)",
    price: "Rs. 119,900",
    priceNum: 119900,
    image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80",
    category: "LED TVs"
  },
  "led-2": {
    id: "led-2",
    brand: "Sony",
    title: "Sony Bravia 43\" Full HD LED TV (W6600)",
    price: "Rs. 138,000",
    priceNum: 138000,
    image: "https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80",
    category: "LED TVs"
  },
  "led-3": {
    id: "led-3",
    brand: "LG",
    title: "LG 43\" Full HD Smart LED TV (LM5750 Series)",
    price: "Rs. 125,000",
    priceNum: 125000,
    image: "https://images.unsplash.com/photo-1552975084-6e027cd345c2?auto=format&fit=crop&w=800&q=80",
    category: "LED TVs"
  },
  "led-4": {
    id: "led-4",
    brand: "TCL",
    title: "TCL 40\" Full HD Google Smart LED TV (S5400)",
    price: "Rs. 89,900",
    priceNum: 89900,
    image: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80",
    category: "LED TVs"
  },
  "led-5": {
    id: "led-5",
    brand: "Hisense",
    title: "Hisense 32\" HD Smart LED TV (A4K Series)",
    price: "Rs. 54,900",
    priceNum: 54900,
    image: "https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=800&q=80",
    category: "LED TVs"
  },

  // Accessories
  "acc-1": {
    id: "acc-1",
    brand: "Samsung",
    title: "Samsung 3.1.2ch Dolby Atmos Soundbar (HW-Q600C)",
    price: "Rs. 89,900",
    priceNum: 89900,
    image: "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80",
    category: "Accessories"
  },
  "acc-2": {
    id: "acc-2",
    brand: "Sony",
    title: "Sony HT-S20R 5.1ch Surround Soundbar System (400W)",
    price: "Rs. 68,000",
    priceNum: 68000,
    image: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80",
    category: "Accessories"
  },
  "acc-3": {
    id: "acc-3",
    brand: "North Bayou",
    title: "North Bayou NB-P6 Full Motion Cantilever Wall Mount (45\"-75\")",
    price: "Rs. 14,500",
    priceNum: 14500,
    image: "https://images.unsplash.com/photo-1584905066893-7d5c142ba4e1?auto=format&fit=crop&w=800&q=80",
    category: "Accessories"
  },
  "acc-4": {
    id: "acc-4",
    brand: "Baseus",
    title: "Baseus 8K Ultra High Speed HDMI 2.1 Cable (3m, 48Gbps)",
    price: "Rs. 4,900",
    priceNum: 4900,
    image: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
    category: "Accessories"
  },
  "acc-5": {
    id: "acc-5",
    brand: "TeleBuy",
    title: "Universal Voice Air-Mouse Remote with Backlit Keyboard",
    price: "Rs. 3,500",
    priceNum: 3500,
    image: "https://images.unsplash.com/photo-1735212769704-d03b95dd1a14?auto=format&fit=crop&w=800&q=80",
    category: "Accessories"
  }
};

// Storage Keys
const CART_KEY = "telebuy_cart";
const WISHLIST_KEY = "telebuy_wishlist";

// ==========================================
// CART API
// ==========================================
function getCart() {
  try {
    const raw = localStorage.getItem(CART_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error("Failed to read cart from localStorage", e);
    return [];
  }
}

function saveCart(cart) {
  try {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    updateHeaderBadges();
  } catch (e) {
    console.error("Failed to save cart to localStorage", e);
  }
}

function addToCart(productId, qty = 1, fallbackObj = null) {
  let itemData = TELEBUY_CATALOG[productId] || fallbackObj;
  if (!itemData) {
    console.warn("Product data not found for id:", productId);
    return;
  }

  const cart = getCart();
  const existingIdx = cart.findIndex(item => item.id === productId);

  if (existingIdx > -1) {
    cart[existingIdx].qty += qty;
  } else {
    cart.push({
      id: itemData.id,
      title: itemData.title,
      brand: itemData.brand || "TeleBuy",
      price: itemData.price,
      priceNum: itemData.priceNum || parseInt(String(itemData.price).replace(/[^0-9]/g, ""), 10) || 0,
      image: itemData.image,
      category: itemData.category || "Televisions",
      qty: qty
    });
  }

  saveCart(cart);
  showToast(`✓ Added ${qty > 1 ? qty + "x " : ""}"${itemData.title}" to cart!`, "cart");
}

function updateCartQty(productId, delta) {
  const cart = getCart();
  const idx = cart.findIndex(item => item.id === productId);
  if (idx > -1) {
    cart[idx].qty += delta;
    if (cart[idx].qty <= 0) {
      cart.splice(idx, 1);
      showToast("Item removed from cart", "trash");
    }
    saveCart(cart);
  }
}

function removeFromCart(productId) {
  const cart = getCart().filter(item => item.id !== productId);
  saveCart(cart);
  showToast("Item removed from cart", "trash");
}

function clearCart() {
  saveCart([]);
  showToast("Cart has been cleared", "trash");
}

function getCartTotalCount() {
  const cart = getCart();
  return cart.reduce((acc, item) => acc + (item.qty || 1), 0);
}

function getCartSubtotal() {
  const cart = getCart();
  return cart.reduce((acc, item) => acc + (item.priceNum * item.qty), 0);
}

// ==========================================
// WISHLIST API
// ==========================================
function getWishlist() {
  try {
    const raw = localStorage.getItem(WISHLIST_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error("Failed to read wishlist from localStorage", e);
    return [];
  }
}

function saveWishlist(wishlist) {
  try {
    localStorage.setItem(WISHLIST_KEY, JSON.stringify(wishlist));
    updateHeaderBadges();
    syncHeartButtons();
  } catch (e) {
    console.error("Failed to save wishlist to localStorage", e);
  }
}

function isInWishlist(productId) {
  const wishlist = getWishlist();
  return wishlist.some(item => item.id === productId);
}

function toggleWishlist(productId, fallbackObj = null) {
  const itemData = TELEBUY_CATALOG[productId] || fallbackObj;
  if (!itemData) return;

  const wishlist = getWishlist();
  const existingIdx = wishlist.findIndex(item => item.id === productId);

  if (existingIdx > -1) {
    wishlist.splice(existingIdx, 1);
    saveWishlist(wishlist);
    showToast(`Removed "${itemData.title}" from your wishlist`, "heart-off");
    return false;
  } else {
    wishlist.push({
      id: itemData.id,
      title: itemData.title,
      brand: itemData.brand || "TeleBuy",
      price: itemData.price,
      priceNum: itemData.priceNum || parseInt(String(itemData.price).replace(/[^0-9]/g, ""), 10) || 0,
      image: itemData.image,
      category: itemData.category || "Televisions"
    });
    saveWishlist(wishlist);
    showToast(`♥ Added "${itemData.title}" to your wishlist!`, "heart");
    return true;
  }
}

function removeFromWishlist(productId) {
  const wishlist = getWishlist().filter(item => item.id !== productId);
  saveWishlist(wishlist);
  showToast("Removed from wishlist", "heart-off");
}

// ==========================================
// UI SYNCHRONIZATION
// ==========================================
function updateHeaderBadges() {
  const cartCount = getCartTotalCount();
  const wishlistCount = getWishlist().length;

  document.querySelectorAll(".cart-badge").forEach(el => {
    el.textContent = cartCount;
    el.style.display = cartCount > 0 ? "flex" : "none";
  });

  document.querySelectorAll(".wishlist-badge").forEach(el => {
    el.textContent = wishlistCount;
    el.style.display = wishlistCount > 0 ? "flex" : "none";
  });
}

function syncHeartButtons() {
  const wishlist = getWishlist();
  const wishlistIds = new Set(wishlist.map(i => i.id));

  document.querySelectorAll(".card-wishlist-btn").forEach(btn => {
    const id = btn.getAttribute("data-id");
    if (wishlistIds.has(id)) {
      btn.classList.add("active");
      btn.setAttribute("aria-label", "Remove from wishlist");
    } else {
      btn.classList.remove("active");
      btn.setAttribute("aria-label", "Add to wishlist");
    }
  });
}

// Universal Toast Notification
function showToast(message, type = "info") {
  let toast = document.getElementById("telebuyToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "telebuyToast";
    toast.className = "toast-notification";
    toast.innerHTML = `<span class="toast-icon">✓</span><span class="toast-text"></span>`;
    document.body.appendChild(toast);
  }

  const icon = toast.querySelector(".toast-icon");
  const text = toast.querySelector(".toast-text");

  if (type === "cart") {
    icon.textContent = "🛍️";
    icon.style.background = "#1f6feb";
  } else if (type === "heart") {
    icon.textContent = "♥";
    icon.style.background = "#e11d48";
  } else if (type === "heart-off" || type === "trash") {
    icon.textContent = "✕";
    icon.style.background = "#64748b";
  } else {
    icon.textContent = "✓";
    icon.style.background = "#10b981";
  }

  text.textContent = message;
  toast.classList.add("show");

  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}

// ============================================================
// THEME MANAGEMENT (Dark Mode & Light Mode)
// ============================================================
const THEME_KEY = "telebuy_theme";

function getStoredTheme() {
  try {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) return saved;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  } catch (e) {
    return "light";
  }
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch (e) {}
  updateThemeToggleUI();
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || getStoredTheme();
  const next = current === "dark" ? "light" : "dark";
  applyTheme(next);
}

function updateThemeToggleUI() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const isDark = current === "dark";
  document.querySelectorAll(".theme-toggle-btn").forEach(btn => {
    btn.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    btn.setAttribute("title", isDark ? "Switch to light mode" : "Switch to dark mode");
  });
}

// Immediate execution
applyTheme(getStoredTheme());

// Global Event Listeners & Initialization
document.addEventListener("DOMContentLoaded", () => {
  updateHeaderBadges();
  syncHeartButtons();
  updateThemeToggleUI();

  // Theme toggle button clicks
  document.addEventListener("click", (e) => {
    const themeBtn = e.target.closest(".theme-toggle-btn");
    if (themeBtn) {
      e.preventDefault();
      e.stopPropagation();
      toggleTheme();
    }
  });

  // Wishlist heart clicks
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".card-wishlist-btn");
    if (btn) {
      e.preventDefault();
      e.stopPropagation();
      const id = btn.getAttribute("data-id");
      toggleWishlist(id);
    }
  });

  // "Add to Cart" button clicks with data-add-id
  document.addEventListener("click", (e) => {
    const addBtn = e.target.closest("[data-add-id]");
    if (addBtn) {
      e.preventDefault();
      e.stopPropagation();
      const id = addBtn.getAttribute("data-add-id");
      const qty = parseInt(addBtn.getAttribute("data-qty") || "1", 10);
      addToCart(id, qty);
    }
  });
});

// Cross-tab synchronization
window.addEventListener("storage", (e) => {
  if (e.key === THEME_KEY) {
    applyTheme(e.newValue || "light");
  }
  if (e.key === CART_KEY || e.key === WISHLIST_KEY) {
    updateHeaderBadges();
    syncHeartButtons();
    if (typeof renderCartPage === "function") renderCartPage();
    if (typeof renderWishlistPage === "function") renderWishlistPage();
  }
});
