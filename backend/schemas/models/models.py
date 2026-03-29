"""
models/models.py - SQLAlchemy ORM models
Defines all database tables with proper relationships and constraints.
"""

from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey,
    DateTime, Enum, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.database import Base


class POStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    COMPLETED = "Completed"


class Vendor(Base):
    """
    Vendors table - Stores supplier/vendor information.
    Rating is a float (1.0 - 5.0 scale).
    """
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact = Column(String(200), nullable=False)
    rating = Column(Float, default=0.0)  # 1.0 to 5.0

    # One vendor can have many purchase orders
    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")


class Product(Base):
    """
    Products table - Stores product catalog.
    SKU must be unique across all products.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    unit_price = Column(Float, nullable=False)
    stock_level = Column(Integer, default=0)
    description = Column(Text, nullable=True)  # AI-generated description stored here

    # One product can appear in many PO line items
    order_items = relationship("PurchaseOrderItem", back_populates="product")


class PurchaseOrder(Base):
    """
    PurchaseOrders table - The main order record.
    reference_no is unique and auto-generated (e.g., PO-2024-0001).
    total_amount includes 5% tax applied at creation time.
    """
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    reference_no = Column(String(50), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)  # Includes 5% tax
    status = Column(String(20), default="Pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    vendor = relationship("Vendor", back_populates="purchase_orders")
    items = relationship(
        "PurchaseOrderItem",
        back_populates="purchase_order",
        cascade="all, delete-orphan"
    )


class PurchaseOrderItem(Base):
    """
    PurchaseOrderItems table - Line items for each PO.
    Links a PO to specific products with quantity and price snapshot.
    Price is stored as snapshot (not live product price) to preserve history.
    """
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Snapshot of unit_price at time of order

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", back_populates="order_items")
