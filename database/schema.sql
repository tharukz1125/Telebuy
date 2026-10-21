-- ============================================================
-- TeleBuy.lk E-Commerce Platform — MySQL Database Schema
-- Database Name: telebuy_db
-- Storage Engine: InnoDB
-- Character Set: utf8mb4 / utf8mb4_unicode_ci
-- ============================================================

CREATE DATABASE IF NOT EXISTS `telebuy_db`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `telebuy_db`;

-- ------------------------------------------------------------
-- 1. Categories Table
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `categories` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `slug` VARCHAR(64) NOT NULL UNIQUE,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT NULL,
  `display_order` INT NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_categories_slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 2. Products Table
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `products` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `product_id` VARCHAR(64) NOT NULL UNIQUE, -- Unique code e.g. 'qled-1', 'feat-1'
  `category_id` INT NULL,
  `brand` VARCHAR(80) NOT NULL,
  `model` VARCHAR(120) NULL,
  `title` VARCHAR(255) NOT NULL,
  `price` DECIMAL(12, 2) NOT NULL,
  `stock` INT NOT NULL DEFAULT 15,
  `description` TEXT NULL,
  `image` VARCHAR(500) NOT NULL,
  `badge` VARCHAR(60) NULL,
  `rating_score` DECIMAL(3, 1) NOT NULL DEFAULT 4.8,
  `rating_count` INT NOT NULL DEFAULT 50,
  `is_featured` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_products_category`
    FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX `idx_products_product_id` (`product_id`),
  INDEX `idx_products_category` (`category_id`),
  INDEX `idx_products_brand` (`brand`),
  INDEX `idx_products_is_featured` (`is_featured`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 3. Users Table (Customer & Admin Accounts)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` VARCHAR(64) NOT NULL UNIQUE, -- Public identifier e.g. 'usr_171000...'
  `full_name` VARCHAR(150) NOT NULL,
  `email` VARCHAR(191) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` VARCHAR(30) NOT NULL DEFAULT 'customer', -- 'customer' or 'admin'
  `phone` VARCHAR(50) NULL,
  `avatar` VARCHAR(500) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_users_email` (`email`),
  INDEX `idx_users_user_id` (`user_id`),
  INDEX `idx_users_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 4. Shipping Addresses Table
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `shipping_addresses` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NULL,
  `recipient_name` VARCHAR(150) NOT NULL,
  `phone` VARCHAR(50) NOT NULL,
  `street` VARCHAR(255) NOT NULL,
  `city` VARCHAR(100) NOT NULL,
  `state` VARCHAR(100) NULL DEFAULT 'Western Province',
  `postal_code` VARCHAR(20) NULL DEFAULT '00300',
  `country` VARCHAR(60) NOT NULL DEFAULT 'Sri Lanka',
  `is_default` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_addresses_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX `idx_addresses_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 5. Cart Items Table (Persistent Cart per User/Session)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `cart_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NULL,
  `session_token` VARCHAR(128) NULL,
  `product_id` VARCHAR(64) NOT NULL,
  `quantity` INT NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_cart_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cart_product`
    FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX `idx_cart_user_id` (`user_id`),
  INDEX `idx_cart_session_token` (`session_token`),
  INDEX `idx_cart_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 6. Orders Table
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `orders` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order_id` VARCHAR(64) NOT NULL UNIQUE, -- Format e.g. 'TB-2026-99979'
  `user_id` INT NULL,
  `customer_name` VARCHAR(150) NOT NULL,
  `customer_email` VARCHAR(191) NOT NULL,
  `customer_phone` VARCHAR(50) NOT NULL,
  `shipping_address` TEXT NOT NULL,
  `subtotal` DECIMAL(12, 2) NOT NULL,
  `delivery_fee` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
  `total_amount` DECIMAL(12, 2) NOT NULL,
  `currency` VARCHAR(10) NOT NULL DEFAULT 'LKR',
  `payment_method` VARCHAR(30) NOT NULL, -- 'payhere' or 'cod'
  `payment_status` VARCHAR(30) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'PAID', 'PENDING_COD', 'CANCELLED', 'FAILED'
  `order_status` VARCHAR(50) NOT NULL DEFAULT 'Pending Payment',
  `delivery_status` VARCHAR(50) NOT NULL DEFAULT 'Order Placed',
  `payhere_payment_id` VARCHAR(100) NULL,
  `tracking_number` VARCHAR(100) NULL,
  `courier_name` VARCHAR(100) NULL,
  `estimated_delivery` VARCHAR(120) NULL,
  `delivery_notes` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_orders_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX `idx_orders_order_id` (`order_id`),
  INDEX `idx_orders_customer_email` (`customer_email`),
  INDEX `idx_orders_user_id` (`user_id`),
  INDEX `idx_orders_payment_status` (`payment_status`),
  INDEX `idx_orders_delivery_status` (`delivery_status`),
  INDEX `idx_orders_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 7. Order Items Table
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `order_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order_id` INT NOT NULL,
  `product_id` VARCHAR(64) NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `brand` VARCHAR(80) NULL,
  `image` VARCHAR(500) NULL,
  `qty` INT NOT NULL DEFAULT 1,
  `unit_price` DECIMAL(12, 2) NOT NULL,
  `line_total` DECIMAL(12, 2) NOT NULL,
  CONSTRAINT `fk_order_items_order`
    FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX `idx_order_items_order_id` (`order_id`),
  INDEX `idx_order_items_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 8. Payments Table
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `payments` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order_id` INT NOT NULL,
  `payment_id` VARCHAR(100) NOT NULL, -- PayHere payment_id or ref
  `method` VARCHAR(50) NOT NULL, -- 'VISA', 'MASTER', 'COD', etc.
  `amount` DECIMAL(12, 2) NOT NULL,
  `currency` VARCHAR(10) NOT NULL DEFAULT 'LKR',
  `status_code` VARCHAR(20) NOT NULL, -- '2', '0', '-1', '-2'
  `status_name` VARCHAR(50) NOT NULL, -- 'SUCCESS', 'PENDING', 'CANCELLED', 'FAILED'
  `raw_response` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_payments_order`
    FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX `idx_payments_order_id` (`order_id`),
  INDEX `idx_payments_payment_id` (`payment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 9. Order Status History Table (Audit log for 7 stages)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `order_status_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order_id` INT NOT NULL,
  `stage` VARCHAR(60) NOT NULL,
  `description` TEXT NULL,
  `updated_by` VARCHAR(100) NOT NULL DEFAULT 'System',
  `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_history_order`
    FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX `idx_history_order_id` (`order_id`),
  INDEX `idx_history_stage` (`stage`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
