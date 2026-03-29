from sqlalchemy.orm import Session, joinedload
from models.models import PurchaseOrder, PurchaseOrderItem, Product, POStatus
from schemas.schemas import PurchaseOrderCreate
from services.vendor_service import get_vendor_by_id
from fastapi import HTTPException
from datetime import datetime
import random, string

TAX_RATE = 0.05

def _generate_reference_no(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    for _ in range(10):
        suffix = "".join(random.choices(string.digits, k=4))
        ref = f"PO-{today}-{suffix}"
        if not db.query(PurchaseOrder).filter(PurchaseOrder.reference_no == ref).first():
            return ref
    raise HTTPException(status_code=500, detail="Could not generate unique reference number.")

def create_purchase_order(db: Session, po_data: PurchaseOrderCreate) -> PurchaseOrder:
    get_vendor_by_id(db, po_data.vendor_id)
    line_items = []
    subtotal = 0.0
    for item in po_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found.")
        if product.stock_level < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for '{product.name}'. Requested: {item.quantity}, Available: {product.stock_level}.")
        line_items.append({"product": product, "quantity": item.quantity, "price": product.unit_price})
        subtotal += item.quantity * product.unit_price
    total_amount = round(subtotal * (1 + TAX_RATE), 2)
    try:
        po = PurchaseOrder(reference_no=_generate_reference_no(db), vendor_id=po_data.vendor_id, total_amount=total_amount, status=POStatus.PENDING)
        db.add(po)
        db.flush()
        for li in line_items:
            po_item = PurchaseOrderItem(po_id=po.id, product_id=li["product"].id, quantity=li["quantity"], price=li["price"])
            db.add(po_item)
            li["product"].stock_level -= li["quantity"]
        db.commit()
        db.refresh(po)
        return db.query(PurchaseOrder).options(joinedload(PurchaseOrder.vendor), joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)).filter(PurchaseOrder.id == po.id).first()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create purchase order: {str(e)}")

def get_all_purchase_orders(db: Session) -> list:
    try:
        return db.query(PurchaseOrder).options(joinedload(PurchaseOrder.vendor), joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)).order_by(PurchaseOrder.created_at.desc()).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch purchase orders: {str(e)}")

def get_purchase_order_by_id(db: Session, po_id: int) -> PurchaseOrder:
    try:
        po = db.query(PurchaseOrder).options(joinedload(PurchaseOrder.vendor), joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)).filter(PurchaseOrder.id == po_id).first()
        if not po:
            raise HTTPException(status_code=404, detail=f"Purchase Order with id {po_id} not found.")
        return po
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch purchase order: {str(e)}")
