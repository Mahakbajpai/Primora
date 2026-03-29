import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DATABASE_URL", "")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base
from routes import vendors, products, purchase_orders

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Primora", version="1.0.0", docs_url="/api/docs")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(vendors.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(purchase_orders.router, prefix="/api")

frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
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
def health():
    return {"status": "ok"}
