# 📦 POMS — Purchase Order Management System

A production-quality mini ERP system for managing Vendors, Products, and Purchase Orders. Built with **FastAPI + PostgreSQL + SQLAlchemy + Vanilla JS**.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Git

### 1. Clone & Setup
```bash
git clone <your-repo-url>
cd po-management

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create the database
createdb po_management

# Load schema + seed data
psql -U postgres -d po_management -f schema.sql
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and set your DATABASE_URL
```

### 4. Run the Server
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser at **http://localhost:8000**

---

## 📁 Project Structure

```
po-management/
│
├── backend/
│   ├── main.py               # FastAPI app entry point
│   ├── database.py           # SQLAlchemy engine & session
│   ├── models/
│   │   └── models.py         # ORM table definitions
│   ├── schemas/
│   │   └── schemas.py        # Pydantic request/response models
│   ├── routes/
│   │   ├── vendors.py        # GET/POST /api/vendors
│   │   ├── products.py       # GET/POST /api/products
│   │   └── purchase_orders.py# GET/POST /api/purchase-orders
│   └── services/
│       ├── vendor_service.py # Vendor business logic
│       ├── product_service.py# Product business logic
│       └── po_service.py     # PO business logic (tax, stock)
│
├── frontend/
│   ├── css/
│   │   └── styles.css        # Dark industrial theme
│   ├── js/
│   │   └── api.js            # Shared API client + helpers
│   └── pages/
│       ├── index.html        # Login page
│       ├── dashboard.html    # PO list + stats
│       ├── create_po.html    # Dynamic PO creation form
│       └── receipt.html      # Order confirmation/receipt
│
├── schema.sql                # PostgreSQL DDL + seed data
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🗄️ Database Design

### Entity Relationship

```
vendors (1) ─────────── (N) purchase_orders (1) ─────────── (N) purchase_order_items
                                                                         │
products (1) ─────────────────────────────────────────────────────── (N) ┘
```

### Design Decisions

| Decision | Reasoning |
|---|---|
| `purchase_order_items.price` stores snapshot | Product prices change over time. Snapshotting at order creation preserves accurate billing history |
| `total_amount` stored (not computed) | Avoids recalculating tax on every read; ensures the agreed total is immutable |
| `ON DELETE RESTRICT` for vendor FK | Prevents accidental deletion of a vendor that has open orders |
| `ON DELETE CASCADE` for PO items | Deleting a PO removes its line items atomically |
| Stock validated before any DB write | Prevents partial orders; all-or-nothing stock deduction |
| Random 4-digit suffix in ref no | Avoids sequential enumeration of PO IDs via public reference |

### Tables

**vendors** — Supplier master  
`id` · `name` · `contact` · `rating (0–5)`

**products** — Product catalog  
`id` · `name` · `sku (UNIQUE)` · `unit_price` · `stock_level` · `description`

**purchase_orders** — PO header  
`id` · `reference_no (UNIQUE)` · `vendor_id (FK)` · `total_amount` · `status` · `created_at`

**purchase_order_items** — PO line items  
`id` · `po_id (FK)` · `product_id (FK)` · `quantity` · `price (snapshot)`

---

## 🔌 API Reference

Base URL: `http://localhost:8000/api`  
Interactive docs: `http://localhost:8000/api/docs`

### Vendors

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/vendors` | List all vendors. `?search=` for filtering |
| `GET` | `/vendors/{id}` | Get single vendor |
| `POST` | `/vendors` | Create vendor |

**Create Vendor**
```json
POST /api/vendors
{
  "name": "Acme Supplies",
  "contact": "sales@acme.com",
  "rating": 4.5
}
```

### Products

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/products` | List all products |
| `GET` | `/products/{id}` | Get single product |
| `POST` | `/products` | Create product |
| `POST` | `/products/ai-description` | Generate AI description |

**Create Product**
```json
POST /api/products
{
  "name": "Industrial Drill Bit",
  "sku": "DRILL-001",
  "unit_price": 2999.00,
  "stock_level": 100
}
```

**AI Description**
```json
POST /api/products/ai-description
{
  "product_name": "Industrial Drill Bit",
  "category": "Tools"
}
```

### Purchase Orders

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/purchase-orders` | List all POs (with vendor + items) |
| `GET` | `/purchase-orders/{id}` | Get single PO |
| `POST` | `/purchase-orders` | Create new PO |

**Create PO**
```json
POST /api/purchase-orders
{
  "vendor_id": 1,
  "items": [
    { "product_id": 1, "quantity": 5 },
    { "product_id": 3, "quantity": 2 }
  ]
}
```

**Response includes auto-calculated totals:**
```json
{
  "id": 1,
  "reference_no": "PO-20240115-7823",
  "total_amount": 16537.50,
  "status": "Pending",
  ...
}
```

---

## 💡 Business Logic

### Total Calculation
```
subtotal     = Σ (quantity × unit_price)
tax          = subtotal × 0.05          ← 5% tax
total_amount = subtotal + tax
```

### Stock Validation Flow
```
For each item in order:
  1. Fetch product from DB
  2. If product.stock_level < requested quantity → return HTTP 400
After all items pass validation:
  3. Create PO record
  4. Create all line items
  5. Deduct stock atomically
  6. Commit transaction
```

---

## 🎨 Frontend Pages

| URL | Page |
|---|---|
| `/` | Login (demo credentials pre-filled) |
| `/dashboard` | All POs, stats, vendor/product panels |
| `/create-po` | Dynamic PO form with add/remove rows |
| `/receipt/{id}` | Order confirmation with printable receipt |

---

## ✨ Features Implemented

- [x] Full CRUD for Vendors and Products
- [x] Purchase Order creation with multiple line items
- [x] Auto 5% tax calculation stored in `total_amount`
- [x] Stock validation and atomic deduction
- [x] Dynamic add/remove product rows in frontend
- [x] Real-time order summary panel (subtotal, tax, total)
- [x] Vendor search (debounced, case-insensitive)
- [x] AI product description via Anthropic API (with fallback)
- [x] Receipt page with printable view
- [x] Dark industrial UI theme
- [x] 20% discount banner (first-time user UI)
- [x] Toast notifications for all actions
- [x] API documentation at `/api/docs`

---

## 🔒 Authentication Note

The system includes a simple session-based demo login. For production:
1. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
2. Install `authlib` and `python-jose[cryptography]`
3. Implement the OAuth2 flow in `routes/auth.py`

The frontend currently uses `sessionStorage` to simulate an auth session for demo purposes.

---

## 🤝 Submission Checklist

- [x] GitHub repository with clean commits
- [x] `schema.sql` with DDL + seed data
- [x] `README.md` with setup instructions
- [x] API documented at `/api/docs` (Swagger UI)
- [ ] 2-minute video demo (record using OBS or Loom)

---

*Built with FastAPI, PostgreSQL, SQLAlchemy, Bootstrap (dark theme), and Vanilla JS.*
