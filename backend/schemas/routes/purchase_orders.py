"""
routes/purchase_orders.py - API endpoints for Purchase Order management.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.schemas.schemas import PurchaseOrderCreate, PurchaseOrderResponse
from backend.services import po_service

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.post("/", response_model=PurchaseOrderResponse, status_code=201)
def create_purchase_order(po: PurchaseOrderCreate, db: Session = Depends(get_db)):
    """
    Create a new Purchase Order.

    Business rules applied automatically:
    - Reference number is auto-generated (PO-YYYYMMDD-XXXX)
    - Total = sum(qty × price) × 1.05  (5% tax)
    - Stock is validated and reduced on success
    - Returns 400 if any product has insufficient stock
    """
    return po_service.create_purchase_order(db, po)


@router.get("/", response_model=List[PurchaseOrderResponse])
def list_purchase_orders(db: Session = Depends(get_db)):
    """Return all Purchase Orders with vendor and item details, newest first."""
    return po_service.get_all_purchase_orders(db)


@router.get("/{po_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    """Get a single Purchase Order with full item breakdown."""
    return po_service.get_purchase_order_by_id(db, po_id)
