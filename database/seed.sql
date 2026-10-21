-- ============================================================
-- TeleBuy.lk E-Commerce Platform — MySQL Seed Data
-- Idempotent insertion using INSERT ... ON DUPLICATE KEY UPDATE
-- ============================================================

USE `telebuy_db`;

-- ------------------------------------------------------------
-- 1. Seed Categories
-- ------------------------------------------------------------
INSERT INTO `categories` (`id`, `slug`, `name`, `description`, `display_order`)
VALUES
  (1, 'qled-tvs', 'QLED TVs', 'Premium Quantum Dot displays with 100% color volume and high peak brightness.', 1),
  (2, 'oled-tvs', 'OLED TVs', 'Self-lit pixel technology offering infinite contrast and true deep blacks.', 2),
  (3, '8k-tvs', '8K Ultra HD TVs', 'Next-generation 8K clarity with AI upscaling for supreme detail.', 3),
  (4, 'smart-tvs', 'Smart TVs', 'Google TV & Tizen powered smart displays with seamless app streaming.', 4),
  (5, 'led-tvs', 'LED TVs', 'Reliable, energy-efficient Full HD & 4K entertainment for every budget.', 5),
  (6, 'accessories', 'TV Accessories', 'Premium Dolby Atmos soundbars, high-speed HDMI cables, and cantilever wall mounts.', 6)
ON DUPLICATE KEY UPDATE
  `name` = VALUES(`name`),
  `description` = VALUES(`description`),
  `display_order` = VALUES(`display_order`);

-- ------------------------------------------------------------
-- 2. Seed Initial Users
-- Admin: admin@telebuy.lk (Password: AdminPass123!)
-- Customer: student@telebuy.lk (Password: Password123!)
-- ------------------------------------------------------------
INSERT INTO `users` (`id`, `user_id`, `full_name`, `email`, `password_hash`, `role`, `phone`, `avatar`)
VALUES
  (1, 'usr_admin_001', 'TeleBuy Administrator', 'admin@telebuy.lk', 'fca918728cfd3dba07689209d958717c10b4e1eda03f470a4017ed96f9119d4d', 'admin', '+94 11 234 5678', 'https://api.dicebear.com/7.x/bottts/svg?seed=Admin'),
  (2, 'usr_student_001', 'Kamal Perera', 'student@telebuy.lk', 'fa8c5cec8d1dcb81669c5f65aeaa607276aafc072f757151e4826c73f42489e1', 'customer', '0771234567', 'https://api.dicebear.com/7.x/bottts/svg?seed=Kamal%20Perera')
ON DUPLICATE KEY UPDATE
  `full_name` = VALUES(`full_name`),
  `password_hash` = VALUES(`password_hash`),
  `role` = VALUES(`role`),
  `phone` = VALUES(`phone`),
  `avatar` = VALUES(`avatar`);

-- ------------------------------------------------------------
-- 3. Seed Default Shipping Addresses
-- ------------------------------------------------------------
INSERT INTO `shipping_addresses` (`id`, `user_id`, `recipient_name`, `phone`, `street`, `city`, `state`, `postal_code`, `country`, `is_default`)
VALUES
  (1, 2, 'Kamal Perera', '0771234567', '45 Galle Road', 'Colombo', 'Western Province', '00300', 'Sri Lanka', 1)
ON DUPLICATE KEY UPDATE
  `recipient_name` = VALUES(`recipient_name`),
  `phone` = VALUES(`phone`),
  `street` = VALUES(`street`),
  `city` = VALUES(`city`),
  `state` = VALUES(`state`),
  `postal_code` = VALUES(`postal_code`);

-- ------------------------------------------------------------
-- 4. Seed Products Catalog (All 34 TV & Audio Models)
-- ------------------------------------------------------------
INSERT INTO `products` (`product_id`, `category_id`, `brand`, `model`, `title`, `price`, `stock`, `description`, `image`, `badge`, `rating_score`, `rating_count`, `is_featured`)
VALUES
  -- Home Featured
  ('feat-1', 1, 'Samsung', 'QA55Q60C', 'Samsung 55" QLED 4K Smart TV', 289900.00, 20, 'Vibrant Quantum Dot display with dual LED backlighting and Quantum HDR for cinematic color.', 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80', 'Featured', 4.8, 120, 1),
  ('feat-2', 2, 'LG', 'OLED55B3', 'LG 55" OLED Smart TV', 524900.00, 15, 'Self-lit OLED pixels delivering perfect black and infinite contrast with Dolby Vision IQ and Atmos.', 'https://images.unsplash.com/photo-1717295248302-543d5a49091f?auto=format&fit=crop&w=800&q=80', 'Editor Choice', 4.9, 95, 1),
  ('feat-3', 5, 'Sony', 'KD-43W6600', 'Sony 43" LED Full HD TV', 134900.00, 30, 'Crisp Full HD resolution powered by X-Reality PRO picture engine with clear sound and smartphone plug-and-play.', 'https://images.unsplash.com/photo-1461151304267-38535e780c79?auto=format&fit=crop&w=800&q=85', 'Best Value', 4.7, 84, 1),
  ('feat-4', 3, 'TCL', '65X925', 'TCL 65" 8K Smart TV', 412900.00, 12, '8K Mini-LED visual masterpiece featuring 33 million pixels with IMAX Enhanced certification.', 'https://images.unsplash.com/photo-1521607630287-ee2e81ad3ced?auto=format&fit=crop&w=800&q=80', 'Flagship', 4.8, 48, 1),

  -- QLED TVs
  ('qled-1', 1, 'Samsung', 'QN65QN90C', 'Samsung 65" Neo QLED 4K Smart TV (QN90C)', 439900.00, 18, 'Quantum Matrix technology with Mini LEDs and Neural Quantum Processor 4K for unimaginable depth.', 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80', 'Best Seller', 4.9, 164, 0),
  ('qled-2', 1, 'Sony', 'XR-55X90L', 'Sony Bravia XR 55" Full Array QLED TV (XR-55X90L)', 385000.00, 15, 'Cognitive Processor XR delivers life-like contrast with XR Triluminos Pro and Acoustic Multi-Audio.', 'https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80', 'Pro Choice', 4.8, 88, 0),
  ('qled-3', 1, 'TCL', '75C845', 'TCL 75" C845 Mini-LED QLED 144Hz Game Master TV', 499900.00, 10, 'Massive 75-inch Mini-LED display with 2000 nits peak brightness and 144Hz VRR gaming mode.', 'https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80', 'Gaming King', 4.9, 72, 0),
  ('qled-4', 1, 'Hisense', '65U8K', 'Hisense 65" U8K Quantum Dot ULED Mini-LED TV', 329900.00, 22, 'Hi-View Engine with Mini-LED PRO and 144Hz Game Mode Pro for thrilling action movies and games.', 'https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=800&q=80', 'Popular', 4.7, 54, 0),
  ('qled-5', 1, 'LG', '55QNED85', 'LG 55" QNED85 Mini-LED Quantum Dot 4K TV', 365000.00, 16, 'Quantum Dot meets NanoCell technology for pure and refined colors with α7 AI Processor Gen6.', 'https://images.unsplash.com/photo-1552975084-6e027cd345c2?auto=format&fit=crop&w=800&q=80', 'New Arrival', 4.8, 41, 0),

  -- OLED TVs
  ('oled-1', 2, 'LG', 'OLED65C3', 'LG 65" OLED evo C3 Series 4K Cinema TV', 549900.00, 14, 'Brightness Booster powered by α9 AI Processor Gen6 with infinite contrast and 0.1ms response time.', 'https://images.unsplash.com/photo-1717295248302-543d5a49091f?auto=format&fit=crop&w=800&q=80', 'Reference Grade', 4.9, 210, 0),
  ('oled-2', 2, 'Sony', 'XR-55A80L', 'Sony Bravia XR 55" A80L OLED Master Series TV', 515000.00, 12, 'Pure OLED black contrast paired with Acoustic Surface Audio+ turns the entire screen into a speaker.', 'https://images.unsplash.com/photo-1717295248230-93ea71f48f92?auto=format&fit=crop&w=800&q=80', 'Master Series', 4.9, 130, 0),
  ('oled-3', 2, 'Samsung', 'QN65S95C', 'Samsung 65" S95C Quantum OLED 4K Flagship TV', 629900.00, 8, 'Quantum Dot OLED merges the inky blacks of OLED with the dazzling peak brightness of Quantum Dots.', 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80', 'Flagship OLED', 5.0, 78, 0),
  ('oled-4', 2, 'Panasonic', 'TH-55MZ2000', 'Panasonic 55" MZ2000 Master OLED Pro Cinema TV', 489900.00, 10, 'Hollywood-tuned Master OLED Pro Cinema panel with custom heat dissipation and 360 Soundscape Pro.', 'https://images.unsplash.com/photo-1521607630287-ee2e81ad3ced?auto=format&fit=crop&w=800&q=80', 'Hollywood Tuned', 4.8, 35, 0),
  ('oled-5', 2, 'LG', 'OLED77G3', 'LG 77" OLED evo G3 Gallery Edition 4K TV', 985000.00, 6, 'Micro Lens Array technology gives up to 70% brighter pictures with a flush-to-wall zero gap design.', 'https://images.unsplash.com/photo-1730909352933-614f1673ac21?auto=format&fit=crop&w=800&q=80', 'Gallery Design', 5.0, 49, 0),

  -- 8K TVs
  ('8k-1', 3, 'Samsung', 'QN75QN900C', 'Samsung 75" Neo QLED 8K TV (QN900C)', 1450000.00, 5, 'Infinity Screen virtually removes borders. Real 8K resolution with 64 AI neural networks.', 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80', '8K Flagship', 4.9, 28, 0),
  ('8k-2', 3, 'Sony', 'XR-75Z9K', 'Sony Bravia XR 75" Z9K Master Series 8K Mini-LED', 1890000.00, 4, 'Master Series 8K Mini-LED precision driven by Cognitive Processor XR with XR Backlight Master Drive.', 'https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80', 'Master Series 8K', 5.0, 19, 0),
  ('8k-3', 3, 'LG', 'OLED77Z3', 'LG 77" Signature OLED 8K TV (Z3 Series)', 2650000.00, 3, 'The zenith of television displays: 8K resolution across 33 million self-lit pixels on a 77-inch canvas.', 'https://images.unsplash.com/photo-1717295248302-543d5a49091f?auto=format&fit=crop&w=800&q=80', 'Signature Ultra', 5.0, 12, 0),
  ('8k-4', 3, 'TCL', '65X925Pro', 'TCL 65" 8K Mini-LED Quantum TV (X925 Pro)', 680000.00, 7, 'OD Zero Mini-LED technology with 8K AI super resolution and Onkyo 5.1.2 sound system.', 'https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80', 'Innovation', 4.8, 22, 0),
  ('8k-5', 3, 'Samsung', 'QN65QN800C', 'Samsung 65" Neo QLED 8K TV (QN800C)', 890000.00, 9, 'Quantum Matrix Pro with slim One Connect box and Dolby Atmos object tracking sound+.', 'https://images.unsplash.com/photo-1521607630287-ee2e81ad3ced?auto=format&fit=crop&w=800&q=80', 'Smart Choice 8K', 4.8, 31, 0),

  -- Smart TVs
  ('smart-1', 4, 'Samsung', 'UA55CU8000', 'Samsung 55" Crystal UHD 4K Smart TV (CU8000)', 219900.00, 25, 'AirSlim design with Dynamic Crystal Color and Samsung Smart Hub for effortless streaming.', 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80', 'Popular', 4.7, 145, 0),
  ('smart-2', 4, 'Sony', 'KD-50X77L', 'Sony Bravia 50" 4K Google TV (KD-50X77L)', 249000.00, 20, '4K Processor X1 with Live Color and Google TV interface with voice-controlled remote.', 'https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80', 'Google TV', 4.8, 98, 0),
  ('smart-3', 4, 'LG', '55UR8050', 'LG 55" 4K UHD Smart TV (UR80 Series)', 235000.00, 22, 'Real 4K clarity with α5 AI Processor 4K Gen6, webOS 23 with personalized quick cards.', 'https://images.unsplash.com/photo-1552975084-6e027cd345c2?auto=format&fit=crop&w=800&q=80', 'Best Seller', 4.8, 112, 0),
  ('smart-4', 4, 'TCL', '50P745', 'TCL 50" P745 4K Google Smart TV', 169900.00, 28, 'Bezel-less metallic design with Wide Color Gamut, Dolby Vision and Dolby Atmos audio.', 'https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80', 'Top Value', 4.7, 76, 0),
  ('smart-5', 4, 'Xiaomi', 'L55M8-A2ME', 'Xiaomi 55" 4K Google TV (A Pro Series)', 159900.00, 30, 'Premium metallic frame, 4K HDR display with MEMC motion smoothing and Chromecast built-in.', 'https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=800&q=80', 'Budget King', 4.7, 89, 0),

  -- LED TVs
  ('led-1', 5, 'Samsung', 'UA43T5300', 'Samsung 43" Full HD Smart LED TV (T5300)', 119900.00, 35, 'Ultra Clean View and PurColor provide high-quality Full HD visuals with built-in Wi-Fi.', 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80', 'Economy', 4.6, 92, 0),
  ('led-2', 5, 'Sony', 'KDL-43W6600', 'Sony Bravia 43" Full HD LED TV (W6600)', 138000.00, 25, 'High Dynamic Range with X-Protection PRO against dust, lightning surges, and humidity.', 'https://images.unsplash.com/photo-1593784991251-92ded75ea290?auto=format&fit=crop&w=800&q=80', 'Durable', 4.7, 65, 0),
  ('led-3', 5, 'LG', '43LM5750', 'LG 43" Full HD Smart LED TV (LM5750 Series)', 125000.00, 26, 'Dynamic Color Enhancer and Virtual Surround Plus bring rich entertainment to compact bedrooms.', 'https://images.unsplash.com/photo-1552975084-6e027cd345c2?auto=format&fit=crop&w=800&q=80', 'Compact Star', 4.6, 58, 0),
  ('led-4', 5, 'TCL', '40S5400', 'TCL 40" Full HD Google Smart LED TV (S5400)', 89900.00, 40, 'FHD resolution powered by Google TV with HDR 10 decoding and dual-band Wi-Fi support.', 'https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&w=800&q=80', 'Super Value', 4.6, 74, 0),
  ('led-5', 5, 'Hisense', '32A4K', 'Hisense 32" HD Smart LED TV (A4K Series)', 54900.00, 50, 'Natural Color Enhancer with DTS Virtual:X sound and VIDAA Smart OS for fast streaming.', 'https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=800&q=80', 'Entry Level', 4.5, 110, 0),

  -- Accessories
  ('acc-1', 6, 'Samsung', 'HW-Q600C', 'Samsung 3.1.2ch Dolby Atmos Soundbar (HW-Q600C)', 89900.00, 25, 'True 3.1.2ch sound with Q-Symphony syncing seamlessly with compatible Samsung television speakers.', 'https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80', 'Dolby Atmos', 4.9, 87, 0),
  ('acc-2', 6, 'Sony', 'HT-S20R', 'Sony HT-S20R 5.1ch Surround Soundbar System (400W)', 68000.00, 30, 'Real 5.1ch surround sound with wired rear speakers, external subwoofer, and 400W total power output.', 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80', '5.1 Surround', 4.8, 105, 0),
  ('acc-3', 6, 'North Bayou', 'NB-P6', 'North Bayou NB-P6 Full Motion Cantilever Wall Mount (45"-75")', 14500.00, 60, 'Heavy-duty steel cantilever mount supports up to 45.5kg with smooth tilt, swivel, and extension.', 'https://images.unsplash.com/photo-1584905066893-7d5c142ba4e1?auto=format&fit=crop&w=800&q=80', 'Heavy Duty', 4.9, 140, 0),
  ('acc-4', 6, 'Baseus', 'HDMI-21-3M', 'Baseus 8K Ultra High Speed HDMI 2.1 Cable (3m, 48Gbps)', 4900.00, 100, 'Certified 48Gbps bandwidth supporting 8K@60Hz and 4K@120Hz with eARC and dynamic HDR pass-through.', 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80', '8K Ultra HDMI', 4.8, 180, 0),
  ('acc-5', 6, 'TeleBuy', 'AIR-REM-01', 'Universal Voice Air-Mouse Remote with Backlit Keyboard', 3500.00, 80, '2.4GHz wireless gyro air-mouse with Google Assistant voice search and full QWERTY keyboard.', 'https://images.unsplash.com/photo-1735212769704-d03b95dd1a14?auto=format&fit=crop&w=800&q=80', 'Accessory', 4.7, 95, 0)
ON DUPLICATE KEY UPDATE
  `title` = VALUES(`title`),
  `brand` = VALUES(`brand`),
  `price` = VALUES(`price`),
  `stock` = VALUES(`stock`),
  `description` = VALUES(`description`),
  `image` = VALUES(`image`),
  `badge` = VALUES(`badge`),
  `category_id` = VALUES(`category_id`),
  `is_featured` = VALUES(`is_featured`);
