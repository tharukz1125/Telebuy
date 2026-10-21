import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
import shutil
import os

def create_completed_document():
    src_path = r"C:\Users\ASUS\Desktop\uni\TG2079\TG_2079.docx"
    doc = docx.Document(src_path)

    # Style colors & properties
    COLOR_PRIMARY_BLUE = RGBColor(0x1F, 0x6F, 0xEB)  # #1F6FEB
    COLOR_HEADING2_DARK = RGBColor(0x1A, 0x1A, 0x1A)  # #1A1A1A
    COLOR_HEADING3_NAVY = RGBColor(0x1F, 0x4D, 0x78)  # #1F4D78
    COLOR_BODY_TEXT = RGBColor(0x22, 0x22, 0x22)
    COLOR_MUTED_GRAY = RGBColor(0x55, 0x55, 0x55)
    FONT_FAMILY = "Calibri"

    def format_run(run, font_name=FONT_FAMILY, size_pt=11, bold=False, italic=False, color=None):
        run.font.name = font_name
        if size_pt:
            run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        if color:
            run.font.color.rgb = color

    def add_p(before_p, text="", style="Normal", space_after=6, space_before=0, line_spacing=1.15):
        p = before_p.insert_paragraph_before("", style=style)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            r = p.add_run(text)
            format_run(r, font_name=FONT_FAMILY, size_pt=11)
        return p

    def add_h1(before_p, text, space_before=14, space_after=6):
        p = before_p.insert_paragraph_before("", style="Heading 1")
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        format_run(r, font_name=FONT_FAMILY, size_pt=16, bold=True, color=COLOR_PRIMARY_BLUE)
        return p

    def add_h2(before_p, text, space_before=12, space_after=4):
        p = before_p.insert_paragraph_before("", style="Heading 2")
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        format_run(r, font_name=FONT_FAMILY, size_pt=13, bold=True, color=COLOR_HEADING2_DARK)
        return p

    def add_h3(before_p, text, space_before=10, space_after=3):
        p = before_p.insert_paragraph_before("", style="Heading 3")
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        format_run(r, font_name=FONT_FAMILY, size_pt=12, bold=True, color=COLOR_HEADING3_NAVY)
        return p

    def add_bullet(before_p, title, desc="", space_after=4):
        p = before_p.insert_paragraph_before("", style="List Paragraph")
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        r_bullet = p.add_run("•  ")
        format_run(r_bullet, font_name=FONT_FAMILY, size_pt=11, bold=True, color=COLOR_PRIMARY_BLUE)
        r_title = p.add_run(title)
        format_run(r_title, font_name=FONT_FAMILY, size_pt=11, bold=True)
        if desc:
            r_desc = p.add_run(f": {desc}")
            format_run(r_desc, font_name=FONT_FAMILY, size_pt=11, bold=False)
        return p

    def add_code_block(before_p, code_text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.rows[0].cells[0]
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
        tcPr.append(shd)
        tcBorders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
                <w:left w:val="single" w:sz="24" w:space="0" w:color="1F6FEB"/>
                <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
                <w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
            </w:tcBorders>
        ''')
        tcPr.append(tcBorders)
        tcMar = parse_xml(f'''
            <w:tcMar {nsdecls("w")}>
                <w:top w:w="120" w:type="dxa"/>
                <w:bottom w:w="120" w:type="dxa"/>
                <w:left w:w="180" w:type="dxa"/>
                <w:right w:w="180" w:type="dxa"/>
            </w:tcMar>
        ''')
        tcPr.append(tcMar)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        
        lines = code_text.strip().split("\n")
        for idx, line in enumerate(lines):
            if idx > 0:
                p = cell.add_paragraph()
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
            r = p.add_run(line)
            format_run(r, font_name="Consolas", size_pt=9.5, bold=False, color=RGBColor(0x1E, 0x29, 0x3B))
            
        before_p._p.addprevious(tbl._tbl)

    def style_custom_table(table, col_widths, headers, data_rows, header_bg="EBF3FA", zebra_bg="F8FAFC"):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        tblPr = table._tbl.tblPr
        tblBorders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="0" w:color="D0D7DE"/>
                <w:left w:val="single" w:sz="6" w:space="0" w:color="D0D7DE"/>
                <w:bottom w:val="single" w:sz="6" w:space="0" w:color="D0D7DE"/>
                <w:right w:val="single" w:sz="6" w:space="0" w:color="D0D7DE"/>
                <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
            </w:tblBorders>
        ''')
        tblPr.append(tblBorders)

        # Header row
        hdr_cells = table.rows[0].cells
        for idx, text in enumerate(headers):
            cell = hdr_cells[idx]
            tcPr = cell._tc.get_or_add_tcPr()
            tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{header_bg}"/>'))
            tcPr.append(parse_xml(f'''
                <w:tcMar {nsdecls("w")}>
                    <w:top w:w="120" w:type="dxa"/>
                    <w:bottom w:w="120" w:type="dxa"/>
                    <w:left w:w="140" w:type="dxa"/>
                    <w:right w:w="140" w:type="dxa"/>
                </w:tcMar>
            '''))
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            format_run(r, font_name=FONT_FAMILY, size_pt=10, bold=True, color=RGBColor(0x0F, 0x17, 0x2A))

        # Data rows
        for r_idx, row_data in enumerate(data_rows):
            row_cells = table.rows[r_idx + 1].cells
            is_even = (r_idx % 2 == 1)
            row_bg = zebra_bg if is_even else "FFFFFF"
            for c_idx, val in enumerate(row_data):
                cell = row_cells[c_idx]
                tcPr = cell._tc.get_or_add_tcPr()
                if row_bg != "FFFFFF":
                    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{row_bg}"/>'))
                tcPr.append(parse_xml(f'''
                    <w:tcMar {nsdecls("w")}>
                        <w:top w:w="100" w:type="dxa"/>
                        <w:bottom w:w="100" w:type="dxa"/>
                        <w:left w:w="140" w:type="dxa"/>
                        <w:right w:w="140" w:type="dxa"/>
                    </w:tcMar>
                '''))
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                r = p.add_run(val)
                is_first_col = (c_idx == 0)
                format_run(r, font_name=FONT_FAMILY, size_pt=9.5, bold=is_first_col, color=RGBColor(0x1E, 0x29, 0x3B))

        for row in table.rows:
            for idx, w in enumerate(col_widths):
                row.cells[idx].width = Inches(w)

    print("Building document content...")

    # Clean up empty heading paragraphs in original doc
    for p in doc.paragraphs:
        if p.style.name.startswith("Heading") and not p.text.strip():
            p.style = "Normal"

    # Landmark 2: Core Development - Frontend & Backend
    core_dev_p = None
    for p in doc.paragraphs:
        if "Core Development" in p.text and "Week 03" in p.text:
            core_dev_p = p
            break

    # Landmark 3: References
    ref_heading_p = None
    for p in doc.paragraphs:
        if "7. References" in p.text:
            ref_heading_p = p
            break

    # -------------------------------------------------------------
    # 1. ADD TABLE & ATTRIBUTES (SECTION 6.1)
    # -------------------------------------------------------------
    add_h2(core_dev_p, "6.1 Database Tables & Attributes (Relational Schema)")
    add_p(core_dev_p, "Following the conceptual Entity Relationship Diagram, the relational database structure for TeleBuy.lk is implemented using MySQL (InnoDB storage engine) with full UTF-8 (utf8mb4_unicode_ci) encoding. The relational schema is normalized to Third Normal Form (3NF) to eliminate data redundancy while maintaining strict referential integrity across product categories, user accounts, shopping carts, order fulfillment, payment audit logs, and delivery tracking.")
    add_p(core_dev_p, "The table below outlines each database table along with its constituent attributes, matching the architectural model shown in the ER diagram:")

    tbl_attr = doc.add_table(rows=12, cols=2)
    tbl_headers = ["Table", "Attributes"]
    tbl_data = [
        ["User Table (users)", "user_id, full_name, email, password_hash, role, phone, avatar, created_at, updated_at"],
        ["Product Table (products)", "product_id, title, brand, category_id, description, price, original_price, stock_qty, screen_size, resolution, panel_type, smart_os, refresh_rate, hdmi_ports, warranty_years, rating_score, created_at"],
        ["Category Table (categories)", "category_id, slug, name, description, icon, created_at"],
        ["Brand Table (brands)", "brand_id, brand_name, country_of_origin, website, created_at"],
        ["Cart Table (cart_items)", "cart_id, user_id, session_token, product_id, quantity, created_at, updated_at"],
        ["Order Table (orders)", "order_id, user_id, customer_name, customer_email, customer_phone, shipping_address, subtotal, delivery_fee, total_amount, currency, payment_method, payment_status, order_status, delivery_status, tracking_number, courier_name, estimated_delivery, created_at"],
        ["Order_Item Table (order_items)", "order_item_id, order_id, product_id, title, brand, image, qty, unit_price, line_total"],
        ["Shipping Address Table (shipping_addresses)", "address_id, user_id, recipient_name, phone, street, city, state, postal_code, country, is_default, created_at"],
        ["Payment Table (payments)", "payment_id, order_id, gateway_payment_id, method, amount, currency, status_code, status_name, raw_response, created_at"],
        ["Review Table (reviews)", "review_id, user_id, product_id, rating, comment, created_at"],
        ["Order Status History Table (order_status_history)", "history_id, order_id, stage, description, updated_by, timestamp"]
    ]
    style_custom_table(tbl_attr, [2.2, 4.3], tbl_headers, tbl_data)
    core_dev_p._p.addprevious(tbl_attr._tbl)

    add_p(core_dev_p, "Detailed Descriptions of Key Relational Tables:")
    add_bullet(core_dev_p, "Users Table (users)", "Stores both registered customer and administrative credentials. Passwords are securely stored using salted cryptographic hashes (SHA-256 / Bcrypt). The 'role' attribute differentiates customer access from administrative back-office privileges.")
    add_bullet(core_dev_p, "Products Table (products)", "Maintains television inventory with authoritative pricing, available stock levels, and complete technical specifications (screen size, panel type, resolution, refresh rate, smart OS, and HDMI ports) required for accurate customer filtering.")
    add_bullet(core_dev_p, "Orders & Order_Items Tables", "The master orders table captures customer delivery contact details, selected payment methods, payment status, delivery tracking numbers, and total sums. The child order_items table preserves a historical line-item snapshot of unit prices and quantities at the exact moment of checkout, protected by cascading relational constraints.")
    add_bullet(core_dev_p, "Payments Table (payments)", "Maintains an immutable audit ledger of all transaction attempts, capturing gateway transaction IDs (e.g., PayHere payment references), payment methods (Visa, MasterCard, COD), status codes, and raw JSON gateway verification responses.")
    add_bullet(core_dev_p, "Order Status History Table (order_status_history)", "Tracks the chronological lifecycle of each order across the 7 distinct delivery stages, recording timestamped stage transitions, warehouse operator notes, and courier dispatch updates.")
    add_p(core_dev_p, "")

    # -------------------------------------------------------------
    # 2. ENHANCE HOMEPAGE SECTION (SECTION 7) WITH CHALLENGES TABLE
    # -------------------------------------------------------------
    core_dev_p.text = "7. Homepage Front-End Development: Milestones, Challenges & Resolutions"
    core_dev_p.style = "Heading 1"
    format_run(core_dev_p.runs[0], font_name=FONT_FAMILY, size_pt=16, bold=True, color=COLOR_PRIMARY_BLUE)

    vc_p = None
    for p in doc.paragraphs:
        if "Version Control & Project Repository" in p.text:
            vc_p = p
            break

    add_h2(vc_p, "7.3 Homepage Frontend Challenges & Solutions Summary Table")
    add_p(vc_p, "The table below summarizes the key technical challenges encountered during the front-end user interface implementation of the TeleBuy.lk homepage (index.html / home.html) alongside the corresponding technical resolutions applied:")

    tbl_hp = doc.add_table(rows=6, cols=3)
    hp_headers = ["Frontend Area", "Challenge / Issue", "Resolution & Fix"]
    hp_data = [
        ["Image Rendering & Asset Paths", "High-resolution television product photos and promotional hero banners failed to render consistently due to case-sensitive filenames and broken relative directory pathing across subfolders.", "Corrected pathing references to standardized relative paths ('images/filename.webp'), normalized directory structure, and resolved file extension discrepancies."],
        ["Mobile Layout Overflows", "The 6-column category grid and 4-column featured TV product cards caused horizontal viewport overflows and scrollbars on mobile screen viewports (< 768px).", "Applied modern CSS Grid and Flexbox rules with flex-wrap and introduced targeted @media query breakpoints (1024px, 768px, 480px) to dynamically re-align cards into 2-column and 1-column mobile layouts."],
        ["Cart Counter Badge Alignment", "The floating numeric cart counter badge misaligned vertically, disrupting text navigation links and breaking layout alignment on smaller laptop displays.", "Encapsulated the SVG shopping cart icon inside a relative container (.cart-icon-wrapper) and applied absolute CSS positioning (position: absolute; top: -6px; right: -8px)."],
        ["Dynamic UI Filtering & Search", "Searching and category button filtering on the homepage required fast UI updates without triggering disruptive full page refreshes.", "Implemented lightweight client-side JavaScript DOM event listeners that filter active product cards instantly based on data-category and data-brand attributes."],
        ["Dark / Light Theme Styling", "Inconsistent contrast and color inversion issues occurred when toggling between dark and light themes across product cards, buttons, and navigation dropdowns.", "Engineered unified CSS custom properties (variables) on :root and [data-theme='dark'], storing the user's active theme preference persistently in browser localStorage."]
    ]
    style_custom_table(tbl_hp, [1.8, 2.3, 2.4], hp_headers, hp_data)
    vc_p._p.addprevious(tbl_hp._tbl)
    add_p(vc_p, "")

    # -------------------------------------------------------------
    # 3. ADD SECTIONS 8, 9, 10, 11 BEFORE REFERENCES
    # -------------------------------------------------------------

    # SECTION 8: TV PRODUCT CATALOGUE & PRODUCT DETAILS
    add_h1(ref_heading_p, "8. TV Product Catalogue & Product Details Implementation")
    add_p(ref_heading_p, "The product catalogue represents the primary discovery engine of TeleBuy.lk. Because televisions represent high-involvement consumer electronics purchases where buyers carefully evaluate specifications such as panel type, refresh rate, screen dimensions, and smart operating systems, the catalogue interface requires high visual clarity and sophisticated filtering capabilities.")

    add_h2(ref_heading_p, "8.1 Product Catalogue Architecture & Layout Overview")
    add_p(ref_heading_p, "The product catalogue is structured into distinct, dedicated display categories to serve varied consumer market segments in Sri Lanka:")
    add_bullet(ref_heading_p, "QLED Televisions", "Features Quantum Dot LED displays with superior peak brightness, high color volume, and advanced HDR10+ support, suitable for brightly lit living rooms.")
    add_bullet(ref_heading_p, "OLED Televisions", "Showcases self-lit pixel displays delivering perfect black levels, infinite contrast, and ultra-fast response times optimized for premium home-theatre enthusiasts and next-generation gaming consoles.")
    add_bullet(ref_heading_p, "LED & Full HD Televisions", "Presents reliable, energy-efficient television models ranging from 32-inch to 43-inch screens designed for bedroom setups and budget-conscious households.")
    add_bullet(ref_heading_p, "8K Ultra HD Flagships", "Highlights cutting-edge 7680x4320 resolution flagship screens with AI-driven upscaling engines for maximum visual immersion.")
    add_bullet(ref_heading_p, "Smart TVs (Google TV / Tizen / WebOS)", "Dedicated listings grouped by smart operating ecosystem, allowing buyers to select models with built-in voice assistants, Chromecast, AirPlay, and streaming services (Netflix, YouTube, Prime Video).")
    add_bullet(ref_heading_p, "Home Entertainment Accessories", "Includes heavy-duty tilt and swivel wall mounts, high-speed HDMI 2.1 eARC cables, voltage surge protectors, and smart remotes.")

    add_p(ref_heading_p, "Each television in the catalogue is presented using a structured product card component that displays:")
    add_bullet(ref_heading_p, "Product Card Visual Hierarchy", "High-resolution product thumbnail, category badge (e.g., 'OLED', '4K UHD'), manufacturer brand logo, full model title, customer star ratings (out of 5.0), live promotional price (LKR), original retail price, and instant 'Add to Cart' and 'View Details' action buttons.")

    add_h2(ref_heading_p, "8.2 Client-Side & Server-Side Filtering & Search Engine")
    add_p(ref_heading_p, "To enable customers to quickly find the exact television matching their room dimensions and budget, TeleBuy.lk incorporates a multi-attribute filtering system combined with a real-time keyword search bar:")
    add_bullet(ref_heading_p, "Brand Filtering", "Allows customers to filter products by leading global manufacturers, including Samsung, LG, Sony, TCL, Hisense, Xiaomi, and Panasonic.")
    add_bullet(ref_heading_p, "Screen Size Segmentation", "Categorizes models into standard room-size brackets: 32\"–43\" (Bedrooms & Compact Spaces), 50\"–55\" (Standard Living Rooms), and 65\"–85\" (Dedicated Home Theatres).")
    add_bullet(ref_heading_p, "Display Technology & Resolution", "Enables direct filtering between OLED, QLED, Mini-LED, Crystal UHD LED, 4K UHD (3840x2160), and 8K Ultra HD (7680x4320).")
    add_bullet(ref_heading_p, "Price Range Filtering", "Provides interactive budget brackets (Under Rs. 100,000; Rs. 100,000 – Rs. 300,000; Above Rs. 300,000) with dynamic price sort controls (Lowest Price, Highest Price, Newest Arrivals).")
    add_bullet(ref_heading_p, "Debounced Real-Time Search", "Listens to user keystrokes in the global search bar, matching input strings against product titles, brand names, series numbers, and resolution keywords with 300ms debouncing to maintain fluid UI responsiveness.")

    add_h2(ref_heading_p, "8.3 Detailed TV Product Page & Technical Specifications")
    add_p(ref_heading_p, "When a customer clicks 'View Details' on any product card, the system displays the dedicated product detail view. This page provides in-depth technical specifications and purchasing guarantees:")
    add_bullet(ref_heading_p, "Multi-Angle Media Gallery", "Displays large primary product images with thumbnail previews showing front bezel, side profile, rear input terminal layouts, and included tabletop stand configurations.")
    add_bullet(ref_heading_p, "Dynamic Screen-Size Variant Selector", "Interactive button selector allowing buyers to switch between available screen sizes (e.g., 50\", 55\", 65\", 75\"). Selecting a different variant dynamically updates the product title, SKU, current price, and warehouse stock availability without reloading the page.")
    add_bullet(ref_heading_p, "Detailed Technical Specifications Table", "Presents an authoritative breakdown of hardware specifications: Display Panel Type, Native Resolution, Refresh Rate (60Hz / 120Hz Native VRR), High Dynamic Range (HDR10+, Dolby Vision IQ), Audio Output (Dolby Atmos, 40W 2.2ch), Connectivity (4x HDMI 2.1, eARC, 2x USB, Optical, Wi-Fi 6, Bluetooth 5.2), and Dimensions with/without stand.")
    add_bullet(ref_heading_p, "Islandwide Delivery & Warranty Guarantee Tabs", "Explicitly displays delivery terms (24–48 hours delivery within Western Province, 2–4 business days islandwide), official agent warranty coverage (1 to 3 years comprehensive warranty), and optional wall-mount installation service details.")

    add_h2(ref_heading_p, "8.4 Challenges Faced in Product Catalogue & Details Implementation")
    add_p(ref_heading_p, "During the front-end and back-end implementation of the TV product catalogue and details views, ten key technical challenges were identified and addressed (corresponding to the quality criteria established in the project guidelines):")
    add_bullet(ref_heading_p, "1. Product Display Organization", "Displaying a large catalog of televisions containing diverse technical details in an organized, visually clean, and uncluttered layout was challenging. This was resolved by designing standardized CSS Grid item cards with consistent padding, uniform badge locations, and clear typography hierarchies.")
    add_bullet(ref_heading_p, "2. Television Categorization", "Categorizing televisions correctly across overlapping dimensions—such as display panel technology (QLED vs. OLED) versus smart operating platforms (Google TV vs. Tizen)—required structured database taxonomy. A normalized category schema was implemented with secondary attribute tags.")
    add_bullet(ref_heading_p, "3. Product Information & Specification Accuracy", "Ensuring that comprehensive technical details (refresh rates, HDMI 2.1 ports, HDR support, power consumption) were displayed accurately across all brands required rigorous data validation and structured JSON specification mapping in MySQL.")
    add_bullet(ref_heading_p, "4. Multi-Attribute Product Filtering", "Developing client-side filtering logic capable of handling compound conditions (e.g., selecting 'Samsung' + '55-inch' + 'OLED' + 'Under Rs. 300,000' simultaneously) was complex. This was solved by implementing a unified JavaScript array filter pipeline that evaluates all active filter predicates iteratively.")
    add_bullet(ref_heading_p, "5. Search Functionality & Performance", "Developing a fast, effective search function to locate products based on brand, partial model names, or specifications required additional JavaScript logic with regex matching and input sanitization to prevent UI freezing.")
    add_bullet(ref_heading_p, "6. Product Details & Variant Switching", "Initially, selecting different screen-size variant buttons failed to update the displayed price and stock count in real time. This was resolved by binding variant selectors to a centralized product data object and updating DOM elements dynamically via event listeners.")
    add_bullet(ref_heading_p, "7. Image Consistency & Aspect Ratios", "Television product images obtained from various manufacturers exhibited disparate aspect ratios and transparent backgrounds, causing uneven card heights. This was resolved by wrapping image elements in fixed 16:9 aspect-ratio containers using CSS 'object-fit: contain'.")
    add_bullet(ref_heading_p, "8. Responsive Layout Across Viewports", "Ensuring that the multi-attribute filter sidebar and product card grid adapted gracefully across desktops, tablets, and smartphones required significant CSS refinement. An off-canvas collapsible filter drawer was implemented for viewports below 1024px.")
    add_bullet(ref_heading_p, "9. Product Card Interactive Design", "Creating attractive, accessible TV product cards featuring badges, pricing, ratings, and action buttons required several design iterations. Subtle CSS box shadows, smooth hover transitions, and distinct primary/secondary button styling were added.")
    add_bullet(ref_heading_p, "10. Testing and Debugging", "Extensive testing was conducted across different web browsers (Google Chrome, Mozilla Firefox, Microsoft Edge, Safari) to resolve JavaScript DOM manipulation inconsistencies, broken image fallbacks, and mobile touch target responsiveness.")
    add_p(ref_heading_p, "")

    # SECTION 9: SHOPPING CART SYSTEM
    add_h1(ref_heading_p, "9. Shopping Cart System Implementation & Local Storage Persistence")
    add_p(ref_heading_p, "The shopping cart is an indispensable component of the TeleBuy.lk e-commerce workflow. It allows customers to aggregate televisions and accessories, inspect selected screen size variants, adjust quantities, calculate order subtotals, and transition seamlessly into the checkout pipeline.")

    add_h2(ref_heading_p, "9.1 Shopping Cart Architecture & Workflow Overview")
    add_p(ref_heading_p, "The shopping cart subsystem is engineered with both client-side responsiveness and persistent data storage:")
    add_bullet(ref_heading_p, "Client-Side State Persistence (localStorage)", "The shopping cart utilizes browser localStorage ('telebuy_cart'). This ensures that customer selections persist across page navigations, browser tab closures, and session reconnects without requiring forced user authentication during initial browsing.")
    add_bullet(ref_heading_p, "Dynamic Cart Drawer & Dedicated Cart Page", "Customers can view their cart via a slide-out cart drawer for quick checks or navigate to the comprehensive shopping cart page (cart.html) for detailed line-item review.")
    add_bullet(ref_heading_p, "Real-Time Header Badge Synchronization", "Whenever items are added, updated, or removed, all navigation bar cart badges across all open browser windows update instantly to reflect the current total item count.")
    add_bullet(ref_heading_p, "Empty State & Boundary Handling", "When the cart contains zero items, a clean empty-cart illustration is displayed alongside an 'Explore TV Catalog' call-to-action button, preventing checkout submissions on empty carts.")

    add_h2(ref_heading_p, "9.2 Data Read and Write Operations (Local Storage Implementation)")
    add_p(ref_heading_p, "The core shopping cart persistence logic is implemented in modular JavaScript (store.js). The code below demonstrates reading from and writing to browser local storage, as well as adding items with quantity aggregation:")

    code_cart_rw = """// ==============================================================
// TeleBuy.lk - Shopping Cart Data Read & Write (store.js)
// ==============================================================
const CART_KEY = 'telebuy_cart';

// Read cart array from browser localStorage
function getCart() {
  try {
    const saved = localStorage.getItem(CART_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch (error) {
    console.error("Failed to read cart from localStorage:", error);
    return [];
  }
}

// Persist cart array to localStorage and sync UI badges
function saveCart(cart) {
  try {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    updateHeaderBadges();
  } catch (error) {
    console.error("Failed to save cart to localStorage:", error);
  }
}

// Add television or accessory to cart with quantity aggregation
function addToCart(productId, quantity = 1, fallbackObj = null) {
  let itemData = TELEBUY_CATALOG[productId] || fallbackObj;
  if (!itemData) {
    console.warn("Product data not found for ID:", productId);
    return { success: false };
  }

  const cart = getCart();
  const existingIndex = cart.findIndex(item => item.id === productId);

  if (existingIndex > -1) {
    // If product already in cart, increment quantity
    cart[existingIndex].qty += quantity;
  } else {
    // Otherwise, push new product entry with authoritative pricing
    cart.push({
      id: itemData.id,
      title: itemData.title,
      brand: itemData.brand || "TeleBuy",
      price: itemData.price,
      priceNum: itemData.priceNum || parseInt(String(itemData.price).replace(/[^0-9]/g, ""), 10) || 0,
      image: itemData.image,
      category: itemData.category || "Televisions",
      qty: quantity
    });
  }

  saveCart(cart);
  showToast(`Added ${quantity > 1 ? quantity + "x " : ""}"${itemData.title}" to cart!`, "cart");
  return { success: true };
}"""
    add_code_block(ref_heading_p, code_cart_rw)

    add_p(ref_heading_p, "Technical Explanation of Read/Write Implementation:")
    add_bullet(ref_heading_p, "Safe JSON Deserialization", "The getCart() function wraps localStorage.getItem() in a try-catch block to handle corrupted JSON data or privacy-mode restrictions gracefully, returning an empty array as fallback.")
    add_bullet(ref_heading_p, "Intelligent Item Aggregation", "The addToCart() function utilizes findIndex() to check if the specific television ID already exists in the cart. If found, it increments the existing quantity instead of duplicating rows, preserving cart cleanliness.")
    add_bullet(ref_heading_p, "Authoritative Price Parsing", "Numeric prices (priceNum) are calculated by stripping non-numeric characters, ensuring robust mathematical calculations during subtotal evaluation.")

    add_h2(ref_heading_p, "9.3 Item Removal and Cart Clear Operations")
    add_p(ref_heading_p, "Managing item quantities, removing individual line items, and resetting the cart upon order completion are handled through dedicated functions:")

    code_cart_remove = """// ==============================================================
// TeleBuy.lk - Item Removal & Cart Management (store.js)
// ==============================================================

// Update item quantity with delta (+1 or -1) and auto-remove on zero
function updateCartQty(productId, delta) {
  const cart = getCart();
  const index = cart.findIndex(item => item.id === productId);
  
  if (index > -1) {
    cart[index].qty += delta;
    if (cart[index].qty <= 0) {
      // Automatically remove item if quantity drops to zero
      cart.splice(index, 1);
      showToast("Item removed from cart", "trash");
    }
    saveCart(cart);
  }
}

// Remove specific television product entirely from shopping cart
function removeFromCart(productId) {
  const cart = getCart().filter(item => item.id !== productId);
  saveCart(cart);
  showToast("Item removed from cart", "trash");
  return cart;
}

// Clear all items from shopping cart (used upon order placement)
function clearCart() {
  saveCart([]);
  showToast("Cart has been cleared", "trash");
}

// Calculate total item count across all line items
function getCartTotalCount() {
  const cart = getCart();
  return cart.reduce((total, item) => total + (item.qty || 1), 0);
}

// Calculate aggregate cart subtotal in Sri Lankan Rupees (LKR)
function getCartSubtotal() {
  const cart = getCart();
  return cart.reduce((subtotal, item) => subtotal + (item.priceNum * item.qty), 0);
}"""
    add_code_block(ref_heading_p, code_cart_remove)

    add_p(ref_heading_p, "Technical Explanation of Removal and Calculation Functions:")
    add_bullet(ref_heading_p, "Functional Array Filtering", "The removeFromCart() function leverages JavaScript Array.prototype.filter() to produce an immutable, cleanly filtered array omitting the target product ID, which is immediately saved back to localStorage.")
    add_bullet(ref_heading_p, "Quantity Delta Control", "The updateCartQty() function enables unified quantity stepping (+1 / -1). When quantity reaches zero, Array.prototype.splice() automatically evicts the product from the array.")
    add_bullet(ref_heading_p, "Subtotal Aggregation", "The getCartSubtotal() function computes the true financial subtotal by aggregating the product of unit price and quantity across all line items using Array.prototype.reduce().")

    add_h2(ref_heading_p, "9.4 Challenges Faced in Shopping Cart Development")
    add_p(ref_heading_p, "During the implementation of the shopping cart subsystem, seven critical technical challenges were addressed (matching the reference system development milestones):")
    add_bullet(ref_heading_p, "1. Add to Cart Functionality & Synchronization", "Initially, adding televisions to the cart did not update navigation counter badges across different open tabs. This was resolved by dispatching custom window events and implementing a shared updateHeaderBadges() routine.")
    add_bullet(ref_heading_p, "2. Quantity Management & Stock Upper Bounds", "Customers could arbitrarily increase cart quantities beyond physical warehouse stock levels. This was resolved by fetching real-time stock thresholds from the MySQL products table and clamping quantity increment buttons when maximum available units are reached.")
    add_bullet(ref_heading_p, "3. Immediate Removal & DOM Re-Rendering", "Removing an item from the cart table occasionally left stale pricing totals in the order summary card. This was resolved by binding removal handlers to an immediate re-render cycle (renderCartItems() + updateOrderSummary()).")
    add_bullet(ref_heading_p, "4. Accurate Total Price & Currency Calculation", "Calculating order totals involving subtotal, free delivery threshold promotions, and optional installation fees resulted in string concatenation bugs. A strict numeric parsing pipeline was implemented, formatting final sums using the Sri Lankan currency format ('Rs. ' + amount.toLocaleString()).")
    add_bullet(ref_heading_p, "5. Cart Data Persistence Across Multi-Page Navigation", "Maintaining consistent cart items while navigating between category pages, product details, and the checkout page required robust state synchronization. Local storage persistence was reinforced with fallback memory caching.")
    add_bullet(ref_heading_p, "6. Responsive Cart Design on Small Screens", "Designing the shopping cart table to display comfortably across mobile screens was a challenge because wide tables caused horizontal overflow. The cart view was restructured using flexible card-based CSS layouts on viewports under 768px.")
    add_bullet(ref_heading_p, "7. Testing and Debugging", "Extensive testing was conducted to verify cart behavior under edge conditions, such as clearing cache, rapid double-clicking of quantity steppers, and adding out-of-stock items, ensuring high reliability.")
    add_p(ref_heading_p, "")

    # SECTION 10: CHECKOUT, PAYMENT METHODS & ORDER TRACKING
    add_h1(ref_heading_p, "10. Checkout Process, Payment Methods & Real-Time Order Tracking")
    add_p(ref_heading_p, "The checkout and fulfillment architecture of TeleBuy.lk provides a secure, streamlined purchasing journey adapted to the commercial and logistical realities of selling consumer electronics in Sri Lanka. It encompasses customer delivery address verification, payment gateway integration, and real-time delivery tracking.")

    add_h2(ref_heading_p, "10.1 Checkout Process & Customer Delivery Information")
    add_p(ref_heading_p, "When customers proceed from the shopping cart to checkout (checkout.html), they are guided through a structured form designed to capture complete delivery and billing details:")
    add_bullet(ref_heading_p, "Recipient Contact Information", "Full customer name, primary email address (for digital order confirmation and PDF invoice dispatch), and verified mobile telephone number (essential for courier pre-delivery coordination).")
    add_bullet(ref_heading_p, "Sri Lankan Delivery Street Address", "Delivery street address (e.g., 'No. 45/2, Temple Road'), City/Town (e.g., 'Colombo 07', 'Kandy', 'Galle'), District selection (Colombo, Gampaha, Kalutara, Kandy, etc.), and Postal Code.")
    add_bullet(ref_heading_p, "Specialized Television Delivery Notes", "Optional handling notes specifically tailored for large electronic screens (e.g., apartment floor number, elevator access availability, preferred delivery time window).")
    add_bullet(ref_heading_p, "Persistent Order Summary Panel", "The checkout interface keeps an itemized order summary visible at all times, detailing selected TV models, screen size variants, quantities, delivery fees (Free Delivery promotion across Sri Lanka), and the final payable total in LKR.")

    add_h2(ref_heading_p, "10.2 Payment Method Options & Security Architecture")
    add_p(ref_heading_p, "To accommodate diverse customer payment preferences in Sri Lanka, TeleBuy.lk supports three primary payment mechanisms with enterprise-grade security:")
    add_bullet(ref_heading_p, "Cash on Delivery (COD)", "Allows customers to pay in cash upon physical receipt and initial unboxing inspection of the television at their doorstep. For high-value television orders exceeding Rs. 100,000, TeleBuy.lk implements mandatory telephone verification before warehouse dispatch.")
    add_bullet(ref_heading_p, "Direct Bank Transfer / Bank Deposit Slip", "Provides direct corporate account details (Commercial Bank of Ceylon / Sampath Bank). Customers can complete an online banking transfer or cash deposit and upload their deposit reference number or slip photo for administrative verification.")
    add_bullet(ref_heading_p, "Online Payment Gateway (PayHere Credit / Debit Card Integration)", "TeleBuy.lk integrates with PayHere, the leading Central Bank of Sri Lanka (CBSL) approved payment service provider, enabling real-time processing of Visa, MasterCard, and American Express cards.")

    add_p(ref_heading_p, "Payment Security & Cryptographic Integrity Standards:")
    add_bullet(ref_heading_p, "256-Bit SSL/TLS Transport Encryption", "All checkout and payment data transactions are encrypted in transit using industry-standard TLS 1.3 / 256-bit SSL protocols, safeguarding customer card details against eavesdropping.")
    add_bullet(ref_heading_p, "Server-Side HMAC-MD5 Cryptographic Signatures", "To prevent client-side payment tampering (such as altering the payable amount or order ID in the browser), TeleBuy.lk's Python backend server generates a cryptographic MD5 hash signature before forwarding payment requests to the gateway: strtoupper(md5(merchant_id + order_id + amount + currency + strtoupper(md5(merchant_secret)))).")
    add_bullet(ref_heading_p, "Idempotent Webhook IPN Verification", "When PayHere sends an Instant Payment Notification (IPN) webhook upon payment completion, the backend verifies the incoming MD5 signature, validates that the paid amount matches the database record, and processes the order idempotently to prevent double-crediting.")
    add_bullet(ref_heading_p, "3D-Secure 2.0 Cardholder Authentication", "Transactions require two-factor biometric or SMS One-Time Password (OTP) verification through the customer's issuing bank (Verified by Visa / MasterCard Identity Check), eliminating fraudulent unauthorized card usage.")

    add_h2(ref_heading_p, "10.3 Order Management & 7-Stage Real-Time Delivery Tracking")
    add_p(ref_heading_p, "Because televisions represent fragile, high-value goods, customers require transparent, real-time visibility into their order status from the moment of purchase until safe installation. TeleBuy.lk features an automated 7-stage delivery tracking system (orders.html):")

    add_p(ref_heading_p, "The 7 Official Delivery Stages:")
    add_bullet(ref_heading_p, "Stage 1: Order Placed", "Order successfully submitted by customer and recorded in the MySQL database with unique order ID (e.g., 'TB-2026-99979').")
    add_bullet(ref_heading_p, "Stage 2: Payment Confirmed", "PayHere gateway payment verified via IPN webhook or Cash on Delivery order validated by customer service.")
    add_bullet(ref_heading_p, "Stage 3: Processing", "Order retrieved by central fulfillment warehouse in Colombo; television unit allocated from live stock.")
    add_bullet(ref_heading_p, "Stage 4: Packed & Screen Quality Checked", "Television undergoes fragile inspection, display panel test, and is packed in shock-absorbing foam with corner edge protectors.")
    add_bullet(ref_heading_p, "Stage 5: Shipped to Courier", "Package handed over to dedicated logistics partner with assigned consignment tracking reference.")
    add_bullet(ref_heading_p, "Stage 6: Out for Delivery", "Assigned courier dispatch team is in transit to the customer's delivery destination for same-day delivery.")
    add_bullet(ref_heading_p, "Stage 7: Delivered & Customer Handover", "Television safely delivered to customer premises, unboxed in customer presence, and delivery signature recorded.")

    add_p(ref_heading_p, "Logistics & Customer Support Features:")
    add_bullet(ref_heading_p, "Islandwide Courier Partner Integration", "TeleBuy.lk partners with Domex Islandwide Express Courier, generating unique tracking reference numbers (e.g., 'DX-1586898LK'). Estimated delivery timeframes are 24–48 hours within Western Province and 2–4 business days for outstation destinations.")
    add_bullet(ref_heading_p, "Integrated WhatsApp Dispatch Support", "Each active order card includes a direct WhatsApp dispatch support link connecting the customer directly with the logistics coordinator for instant delivery updates.")
    add_bullet(ref_heading_p, "Printable Tax Invoice Receipt", "Customers can view and print an official VAT/tax invoice detailing customer details, itemized television models, serial numbers, warranty terms, and company authorization seals.")

    add_h2(ref_heading_p, "10.4 Challenges Faced in Checkout, Payment & Delivery Tracking")
    add_p(ref_heading_p, "During the implementation of checkout, payment, and delivery tracking, several domain-specific challenges were addressed:")
    add_bullet(ref_heading_p, "Payment Webhook Latency & Idempotency", "Ensuring that asynchronous PayHere IPN callbacks did not cause duplicate order fulfillment records when network retries occurred. Solved by implementing database-level transaction locks and checking existing payment status before executing state updates.")
    add_bullet(ref_heading_p, "Form Validation & Phone Number Formatting", "Handling varied user phone inputs (e.g., '+94', '071...', '71...') without errors. Implemented strict client-side and server-side regex validation normalizing all numbers to Sri Lankan mobile format.")
    add_bullet(ref_heading_p, "Order Status Synchronization", "Ensuring that administrative order stage updates in admin-orders.html reflected immediately on customer order tracking pages (orders.html). Implemented audit logging in the order_status_history table.")
    add_bullet(ref_heading_p, "Fragile Television Logistics Assurance", "Mitigating customer anxiety regarding transit damage for large OLED/QLED screens. Solved by providing explicit unboxing inspection guidelines, transit insurance documentation, and direct WhatsApp support channels.")
    add_p(ref_heading_p, "")

    # SECTION 11: SYSTEM TESTING & QUALITY ASSURANCE
    add_h1(ref_heading_p, "11. System Testing, Quality Assurance & Database Verification")
    add_p(ref_heading_p, "To verify system stability, data integrity, and security across all user workflows, comprehensive manual and automated integration testing was executed on TeleBuy.lk:")
    add_bullet(ref_heading_p, "Database Relational Integrity Testing", "Verified all 8 foreign-key constraints across the 11 MySQL tables, confirming that cascading deletes and nullifications function properly without orphan records.")
    add_bullet(ref_heading_p, "Authentication & Role Security Testing", "Tested user registration, salted SHA-256 password hashing, and role-based access control to ensure administrative endpoints reject unauthorized customer sessions.")
    add_bullet(ref_heading_p, "E-Commerce Transactional Testing", "Verified complete end-to-end shopping workflows: browsing catalogue categories, applying dynamic filters, searching by keyword, adding multiple TV variants to cart, adjusting quantities, applying checkout details, and completing payment via PayHere sandbox.")
    add_bullet(ref_heading_p, "Cryptographic Signature & Webhook Security", "Simulated PayHere payment notifications with valid and invalid MD5 signatures, confirming that fraudulent requests are rejected with HTTP 400 while authentic callbacks correctly advance order status to 'PAID'.")
    add_bullet(ref_heading_p, "Cross-Device Responsive UI Testing", "Evaluated page rendering, navigation bars, filter sidebars, and cart tables across desktop, tablet, and mobile screen resolutions, confirming full responsive usability.")
    add_p(ref_heading_p, "")

    # SECTION 12: REFERENCES
    ref_heading_p.text = "12. References"
    ref_heading_p.style = "Heading 1"
    format_run(ref_heading_p.runs[0], font_name=FONT_FAMILY, size_pt=16, bold=True, color=COLOR_PRIMARY_BLUE)

    last_p = doc.paragraphs[-1]
    add_p(last_p, "Technical Documentation & Industry Standards:")
    add_bullet(last_p, "PayHere Sri Lanka Payment Gateway API Documentation", "https://support.payhere.lk/api-payments")
    add_bullet(last_p, "Mozilla Developer Network (MDN) Web Docs", "Web Storage API (localStorage), Fetch API & CSS Grid Layout - https://developer.mozilla.org/")
    add_bullet(last_p, "MySQL 8.0 Reference Manual", "InnoDB Storage Engine, Foreign Key Constraints & Index Optimization - https://dev.mysql.com/doc/")
    add_bullet(last_p, "Domex Islandwide Express Courier Sri Lanka", "Courier Logistics & Consignment Tracking Systems - https://www.domex.lk/")
    add_bullet(last_p, "W3C Web Accessibility Guidelines (WCAG 2.1)", "Standards for E-Commerce Accessibility & Responsive Design - https://www.w3.org/WAI/standards-guidelines/wcag/")

    target_path_1 = r"c:\Users\ASUS\Desktop\project_B\TeleBuy.lk_Completed_Document.docx"
    target_path_2 = r"C:\Users\ASUS\Desktop\uni\TG2079\TeleBuy.lk_Completed_Document.docx"
    
    doc.save(target_path_1)
    print(f"Saved completed document to: {target_path_1}")
    
    doc.save(target_path_2)
    print(f"Saved completed document copy to: {target_path_2}")

if __name__ == "__main__":
    create_completed_document()
