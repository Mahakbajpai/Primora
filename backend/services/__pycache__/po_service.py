"""
services/po_service.py - Core business logic for Purchase Orders.

KEY BUSINESS RULES:
  1. Reference numbers are auto-generated: PO-YYYYMMDD-NNNN
  2. Total = sum(quantity × unit_price) × 1.05  (5% tax applied)
  3. Stock is validated BEFORE order creation (no partial fills)
  4. Stock is REDUCED atomically after successful order creation
"""

from sqlalchemy.orm import Session, joinedload
from backend.models.models import PurchaseOrder, PurchaseOrderItem, Product, POStatus
from backend.schemas.schemas import PurchaseOrderCreate
from backend.services.vendor_service import get_vendor_by_id
from fastapi import HTTPException
from datetime import datetime
import random
import string


TAX_RATE = 0.05  # 5% tax


def _generate_reference_no(db: Session) -> str:
    """
    Generate a unique PO reference number.
    Format: PO-YYYYMMDD-XXXX where XXXX is a random 4-digit suffix.
    Retries if collision detected (extremely unlikely).
    """
    today = datetime.now().strftime("%Y%m%d")
    for _ in range(10):  # Retry up to 10 times on collision
        suffix = "".join(random.choices(string.digits, k=4))
        ref = f"PO-{today}-{suffix}"
        if not db.query(PurchaseOrder).filter(PurchaseOrder.reference_no == ref).first():
            return ref
    raise HTTPException(status_code=500, detail="Could not generate unique reference number.")


def create_purchase_order(db: Session, po_data: PurchaseOrderCreate) -> PurchaseOrder:
    """
    Create a Purchase Order with full business logic:
      - Validate vendor exists
      - Validate all products exist and have sufficient stock
      - Calculate subtotal and apply 5% tax
      - Save PO and line items
      - Deduct stock atomically
    """
    # Step 1: Validate vendor
    get_vendor_by_id(db, po_data.vendor_id)  # Raises 404 if not found

    # Step 2: Load all products and validate stock upfront
    # We do this BEFORE any DB writes so we don't have partial orders
    line_items = []
    subtotal = 0.0

    for item in po_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with id {item.product_id} not found."
            )
        if product.stock_level < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Insufficient stock for '{product.name}'. "
                    f"Requested: {item.quantity}, Available: {product.stock_level}."
                )
            )
        line_items.append({
            "product": product,
            "quantity": item.quantity,
            "price": product.unit_price  # Snapshot current price
        })
        subtotal += item.quantity * product.unit_price

    # Step 3: Calculate total with tax
    total_amount = round(subtotal * (1 + TAX_RATE), 2)

    # Step 4: Create PO record
    try:
        po = PurchaseOrder(
            reference_no=_generate_reference_no(db),
            vendor_id=po_data.vendor_id,
            total_amount=total_amount,
            status=POStatus.PENDING
        )
        db.add(po)
        db.flush()  # Get po.id without committing yet

        # Step 5: Create line items and deduct stock
        for li in line_items:
            po_item = PurchaseOrderItem(
                po_id=po.id,
                product_id=li["product"].id,
                quantity=li["quantity"],
                price=li["price"]
            )
            db.add(po_item)
            li["product"].stock_level -= li["quantity"]  # Deduct stock

        db.commit()
        db.refresh(po)

        # Reload with relationships for full response
        return (
            db.query(PurchaseOrder)
            .options(
                joinedload(PurchaseOrder.vendor),
                joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
            )
            .filter(PurchaseOrder.id == po.id)
            .first()
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create purchase order: {str(e)}")


def get_all_purchase_orders(db: Session) -> list:
    """Return all POs with vendor and items eager-loaded, newest first."""
    try:
        return (
            db.query(PurchaseOrder)
            .options(
                joinedload(PurchaseOrder.vendor),
                joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
            )
            .order_by(PurchaseOrder.created_at.desc())
            .all()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch purchase orders: {str(e)}")


def get_purchase_order_by_id(db: Session, po_id: int) -> PurchaseOrder:
    """Fetch a single PO with all relationships loaded."""
    try:
        po = (
            db.query(PurchaseOrder)
            .options(
                joinedload(PurchaseOrder.vendor),
                joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
            )
            .filter(PurchaseOrder.id == po_id)
            .first()
        )
        if not po:
            raise HTTPException(status_code=404, detail=f"Purchase Order with id {po_id} not found.")
        return po
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch purchase order: {str(e)}")
