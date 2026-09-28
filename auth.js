/**
 * TeleBuy.lk — Authentication & User Profile Management Engine
 * Implements Week 06 Practical Requirements:
 * 1. Password Hashing (SHA-256 via Web Crypto API)
 * 2. User Registration with Regex & Complexity Validation
 * 3. User Authentication with Generic Security Errors
 * 4. Simulated JWT Session Persistence (localStorage)
 * 5. Route Protection & Guards with Return URL
 * 6. Dynamic User Profile, Address Management & Cart Association
 */

// Storage Keys
const AUTH_USERS_KEY = "telebuy_users";
const AUTH_SESSION_KEY = "telebuy_session";

/**
 * -------------------------------------------------------------
 * 1. CRYPTOGRAPHIC UTILITIES (Password Hashing via Web Crypto API)
 * -------------------------------------------------------------
 */
async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password + "_telebuy_salt_2026");
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
  return hashHex;
}

/**
 * -------------------------------------------------------------
 * 2. DATABASE / STORAGE HELPERS
 * -------------------------------------------------------------
 */
function getAllUsers() {
  try {
    const data = localStorage.getItem(AUTH_USERS_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    console.error("Failed to parse users database", e);
    return [];
  }
}

function saveAllUsers(users) {
  try {
    localStorage.setItem(AUTH_USERS_KEY, JSON.stringify(users));
  } catch (e) {
    console.error("Failed to save users database", e);
  }
}

function findUserByEmail(email) {
  if (!email) return null;
  const users = getAllUsers();
  return users.find(u => u.email.toLowerCase().trim() === email.toLowerCase().trim()) || null;
}

function findUserById(userId) {
  if (!userId) return null;
  const users = getAllUsers();
  return users.find(u => u.user_id === userId) || null;
}

/**
 * -------------------------------------------------------------
 * 3. VALIDATION UTILITIES (Regex & Complexity Checks)
 * -------------------------------------------------------------
 */
const VALIDATION = {
  isValidEmail(email) {
    const re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    return re.test(String(email).toLowerCase().trim());
  },
  validatePasswordComplexity(password) {
    // Min 8 chars, at least 1 uppercase, 1 lowercase, 1 number
    const hasMinLength = (password || "").length >= 8;
    const hasUpper = /[A-Z]/.test(password || "");
    const hasLower = /[a-z]/.test(password || "");
    const hasNumber = /[0-9]/.test(password || "");
    const hasSpecial = /[^A-Za-z0-9]/.test(password || "");

    let score = 0;
    if (hasMinLength) score++;
    if (hasUpper && hasLower) score++;
    if (hasNumber) score++;
    if (hasSpecial) score++;

    let strength = "Weak";
    if (score >= 4) strength = "Strong";
    else if (score >= 2) strength = "Medium";

    return {
      isValid: hasMinLength && hasUpper && hasLower && hasNumber,
      strength,
      score,
      errors: [
        !hasMinLength ? "At least 8 characters long" : null,
        !hasUpper ? "At least one uppercase letter (A-Z)" : null,
        !hasLower ? "At least one lowercase letter (a-z)" : null,
        !hasNumber ? "At least one number (0-9)" : null
      ].filter(Boolean)
    };
  }
};

/**
 * -------------------------------------------------------------
 * 4. USER REGISTRATION (Milestone 1)
 * -------------------------------------------------------------
 */
async function registerUser({ fullName, email, password, phone = "", role = "authenticated" }) {
  const cleanName = (fullName || "").trim();
  const cleanEmail = (email || "").trim().toLowerCase();

  if (!cleanName || cleanName.length < 2) {
    return { success: false, message: "Please provide your full name (minimum 2 characters)." };
  }

  if (!VALIDATION.isValidEmail(cleanEmail)) {
    return { success: false, message: "Please provide a valid email address." };
  }

  const complexity = VALIDATION.validatePasswordComplexity(password);
  if (!complexity.isValid) {
    return { 
      success: false, 
      message: `Password requirement not met: ${complexity.errors.join(", ")}` 
    };
  }

  // Check duplicate email
  if (findUserByEmail(cleanEmail)) {
    return { success: false, message: "An account with this email address is already registered." };
  }

  // Hash password
  const passwordHash = await hashPassword(password);
  const now = new Date().toISOString();
  const userId = "usr_" + Date.now() + "_" + Math.floor(Math.random() * 1000);

  const newUser = {
    user_id: userId,
    full_name: cleanName,
    email: cleanEmail,
    password_hash: passwordHash,
    created_at: now,
    role: role,
    avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(cleanName)}`,
    phone: phone,
    shipping_address: {
      street: "",
      city: "Colombo",
      state: "Western Province",
      postal_code: "",
      country: "Sri Lanka"
    },
    billing_address: {
      street: "",
      city: "Colombo",
      state: "Western Province",
      postal_code: "",
      country: "Sri Lanka"
    }
  };

  const users = getAllUsers();
  users.push(newUser);
  saveAllUsers(users);

  return { 
    success: true, 
    message: "Registration successful! You can now log in.",
    user: {
      user_id: newUser.user_id,
      full_name: newUser.full_name,
      email: newUser.email,
      role: newUser.role
    }
  };
}

/**
 * -------------------------------------------------------------
 * 5. USER AUTHENTICATION & LOGIN (Milestone 2)
 * -------------------------------------------------------------
 */
async function loginUser(email, password, rememberMe = true) {
  const cleanEmail = (email || "").trim().toLowerCase();

  // Core Security Rule: Generic error message to prevent user enumeration
  const GENERIC_ERROR = "Invalid email or password. Please check your credentials and try again.";

  if (!cleanEmail || !password) {
    return { success: false, message: GENERIC_ERROR };
  }

  const user = findUserByEmail(cleanEmail);
  if (!user) {
    return { success: false, message: GENERIC_ERROR };
  }

  const inputHash = await hashPassword(password);
  if (inputHash !== user.password_hash) {
    return { success: false, message: GENERIC_ERROR };
  }

  // Create simulated JWT Session
  const sessionDuration = rememberMe ? 7 * 24 * 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
  const expiresAt = Date.now() + sessionDuration;

  const sessionPayload = {
    token: `tb_jwt_${btoa(user.user_id)}.${btoa(JSON.stringify({ sub: user.user_id, email: user.email, role: user.role }))}.${btoa(String(expiresAt))}`,
    user: {
      user_id: user.user_id,
      full_name: user.full_name,
      email: user.email,
      role: user.role,
      avatar: user.avatar || `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(user.full_name)}`
    },
    expires_at: expiresAt
  };

  try {
    localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(sessionPayload));
  } catch (e) {
    console.error("Failed to save auth session", e);
  }

  // Associate / Merge guest cart items
  mergeGuestCartUponLogin(user.user_id);

  // Dispatch auth state change event
  window.dispatchEvent(new CustomEvent("telebuy_auth_change", { detail: sessionPayload }));

  return {
    success: true,
    message: `Welcome back, ${user.full_name}!`,
    session: sessionPayload
  };
}

/**
 * -------------------------------------------------------------
 * 6. SESSION MANAGEMENT & LOGOUT (Milestone 3)
 * -------------------------------------------------------------
 */
function getAuthSession() {
  try {
    const raw = localStorage.getItem(AUTH_SESSION_KEY);
    if (!raw) return null;
    const session = JSON.parse(raw);

    // Check expiration
    if (session.expires_at && Date.now() > session.expires_at) {
      clearAuthSession();
      return null;
    }
    return session;
  } catch (e) {
    return null;
  }
}

function getCurrentUser() {
  const session = getAuthSession();
  if (!session || !session.user) return null;
  return findUserById(session.user.user_id);
}

function isAuthenticated() {
  return getAuthSession() !== null;
}

function logoutUser(redirectUrl = "index.html") {
  clearAuthSession();
  window.dispatchEvent(new CustomEvent("telebuy_auth_change", { detail: null }));
  if (redirectUrl) {
    window.location.href = redirectUrl;
  }
}

function clearAuthSession() {
  try {
    localStorage.removeItem(AUTH_SESSION_KEY);
  } catch (e) {
    console.error("Failed to clear auth session", e);
  }
}

/**
 * -------------------------------------------------------------
 * 7. ROUTE GUARDS / PROTECTED ROUTES (Milestone 3)
 * -------------------------------------------------------------
 */
function requireAuth(customReturnUrl) {
  if (!isAuthenticated()) {
    const returnUrl = customReturnUrl || encodeURIComponent(window.location.pathname.split("/").pop() || "profile.html");
    window.location.href = `login.html?returnUrl=${returnUrl}`;
    return false;
  }
  return true;
}

/**
 * -------------------------------------------------------------
 * 8. CART MERGE / GUEST TO USER ASSOCIATION (Milestone 4)
 * -------------------------------------------------------------
 */
function mergeGuestCartUponLogin(userId) {
  try {
    const cart = typeof getCart === "function" ? getCart() : JSON.parse(localStorage.getItem("telebuy_cart") || "[]");
    if (cart.length > 0) {
      // Guest cart items are retained and active in user session
      console.log(`[TeleBuy Auth] Associated ${cart.length} cart items with user account ${userId}`);
    }
  } catch (e) {
    console.warn("Cart merge failed", e);
  }
}

/**
 * -------------------------------------------------------------
 * 9. USER PROFILE & ADDRESS MANAGEMENT (Milestone 4)
 * -------------------------------------------------------------
 */
function updateUserProfile(userId, { fullName, phone, shippingAddress, billingAddress }) {
  const users = getAllUsers();
  const index = users.findIndex(u => u.user_id === userId);
  if (index === -1) {
    return { success: false, message: "User not found." };
  }

  const user = users[index];

  if (fullName && fullName.trim().length >= 2) {
    user.full_name = fullName.trim();
    user.avatar = `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(user.full_name)}`;
  }

  if (phone !== undefined) {
    user.phone = phone.trim();
  }

  if (shippingAddress) {
    user.shipping_address = { ...user.shipping_address, ...shippingAddress };
  }

  if (billingAddress) {
    user.billing_address = { ...user.billing_address, ...billingAddress };
  }

  users[index] = user;
  saveAllUsers(users);

  // Update session copy
  const session = getAuthSession();
  if (session && session.user && session.user.user_id === userId) {
    session.user.full_name = user.full_name;
    session.user.avatar = user.avatar;
    localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(session));
  }

  window.dispatchEvent(new CustomEvent("telebuy_auth_change", { detail: session }));

  return { success: true, message: "Profile updated successfully!", user };
}

async function changeUserPassword(userId, currentPassword, newPassword) {
  const users = getAllUsers();
  const index = users.findIndex(u => u.user_id === userId);
  if (index === -1) {
    return { success: false, message: "User not found." };
  }

  const user = users[index];
  const currentHash = await hashPassword(currentPassword);

  if (currentHash !== user.password_hash) {
    return { success: false, message: "The current password you entered is incorrect." };
  }

  const complexity = VALIDATION.validatePasswordComplexity(newPassword);
  if (!complexity.isValid) {
    return { 
      success: false, 
      message: `New password requirement not met: ${complexity.errors.join(", ")}` 
    };
  }

  const newHash = await hashPassword(newPassword);
  user.password_hash = newHash;
  users[index] = user;
  saveAllUsers(users);

  return { success: true, message: "Password updated successfully!" };
}

/**
 * -------------------------------------------------------------
 * 10. CLIENT NAVIGATION & NAVBAR AUTH SYNC
 * -------------------------------------------------------------
 */
function renderNavbarAuthState() {
  const session = getAuthSession();
  const authContainers = document.querySelectorAll(".nav-auth-item");

  authContainers.forEach(container => {
    if (session && session.user) {
      const user = session.user;
      const firstName = (user.full_name || "User").split(" ")[0];
      container.innerHTML = `
        <div class="nav-user-dropdown" id="navUserDropdown">
          <button class="nav-user-btn" id="navUserBtn" aria-expanded="false" aria-label="User profile menu">
            <img src="${user.avatar}" alt="${user.full_name}" class="nav-avatar-img">
            <span class="nav-user-name">${firstName}</span>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
          <div class="nav-dropdown-menu" id="navDropdownMenu">
            <div class="dropdown-header">
              <strong>${user.full_name}</strong>
              <small>${user.email}</small>
            </div>
            <a href="profile.html" class="dropdown-link">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <span>Profile &amp; Settings</span>
            </a>
            <a href="wishlist.html" class="dropdown-link">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
              </svg>
              <span>My Wishlist</span>
            </a>
            <div class="dropdown-divider"></div>
            <button class="dropdown-link btn-logout" id="btnLogoutNav" type="button">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      `;

      // Setup dropdown toggle
      const btn = container.querySelector("#navUserBtn");
      const menu = container.querySelector("#navDropdownMenu");
      const logoutBtn = container.querySelector("#btnLogoutNav");

      if (btn && menu) {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const open = menu.classList.toggle("show");
          btn.setAttribute("aria-expanded", open);
        });
      }

      if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
          logoutUser("index.html");
        });
      }
    } else {
      // Unauthenticated state
      container.innerHTML = `
        <a href="login.html" class="nav-login-link" title="Sign In or Register">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
          <span>Sign In</span>
        </a>
      `;
    }
  });
}

// Close dropdown on outside click
document.addEventListener("click", (e) => {
  if (!e.target.closest(".nav-user-dropdown")) {
    document.querySelectorAll(".nav-dropdown-menu.show").forEach(menu => {
      menu.classList.remove("show");
      const btn = menu.parentElement.querySelector(".nav-user-btn");
      if (btn) btn.setAttribute("aria-expanded", "false");
    });
  }
});

// Auto-seed demo student account if database is completely empty
(async function initDemoUser() {
  const users = getAllUsers();
  if (users.length === 0) {
    await registerUser({
      fullName: "Dev Student",
      email: "student@telebuy.lk",
      password: "Password123!",
      phone: "+94 77 123 4567",
      role: "authenticated"
    });
    // Set default demo addresses
    const demo = findUserByEmail("student@telebuy.lk");
    if (demo) {
      demo.shipping_address = {
        street: "45/2 Duplication Road",
        city: "Colombo",
        state: "Western Province",
        postal_code: "00300",
        country: "Sri Lanka"
      };
      demo.billing_address = { ...demo.shipping_address };
      saveAllUsers([demo]);
    }
  }
})();

// Initialize navbar state on DOM load
document.addEventListener("DOMContentLoaded", () => {
  renderNavbarAuthState();
});

// Listen for cross-tab session changes
window.addEventListener("storage", (e) => {
  if (e.key === AUTH_SESSION_KEY) {
    renderNavbarAuthState();
    if (window.location.pathname.endsWith("profile.html") && !isAuthenticated()) {
      window.location.href = "login.html?returnUrl=profile.html";
    }
  }
});

window.addEventListener("telebuy_auth_change", () => {
  renderNavbarAuthState();
});
