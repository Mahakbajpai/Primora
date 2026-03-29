"""
main.py - FastAPI application entry point.
Initializes the app, registers routers, and sets up DB tables.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import engine, Base
from routes import vendors, products, purchase_orders

# Auto-create all tables on startup (use Alembic for production migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Purchase Order Management System",
    description=(
        "A mini ERP system for managing Vendors, Products, and Purchase Orders. "
        "Built with FastAPI + PostgreSQL + SQLAlchemy."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ─────────────────────────────────────────────
# CORS - Allow frontend to talk to backend
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# API ROUTERS
# ─────────────────────────────────────────────
app.include_router(vendors.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(purchase_orders.router, prefix="/api")

# ─────────────────────────────────────────────
# SERVE STATIC FRONTEND
# ─────────────────────────────────────────────
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(frontend_dir, "pages", "index.html"))

    @app.get("/dashboard")
    def serve_dashboard():
        return FileResponse(os.path.join(frontend_dir, "pages", "dashboard.html"))

    @app.get("/create-po")
    def serve_create_po():
        return FileResponse(os.path.join(frontend_dir, "pages", "create_po.html"))

    @app.get("/receipt/{po_id}")
    def serve_receipt(po_id: int):
        return FileResponse(os.path.join(frontend_dir, "pages", "receipt.html"))


@app.get("/api/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}
