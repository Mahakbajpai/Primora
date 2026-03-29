"""
schemas/schemas.py - Pydantic schemas for request validation and response serialization.
Pydantic enforces type safety and provides automatic API documentation.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class POStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    COMPLETED = "Completed"


# ─────────────────────────────────────────────
# VENDOR SCHEMAS
# ─────────────────────────────────────────────

class VendorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, example="Acme Supplies Ltd.")
    contact: str = Field(..., min_length=1, max_length=200, example="contact@acme.com")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, example=4.5)


class VendorResponse(BaseModel):
    id: int
    name: str
    contact: str
    rating: float

    class Config:
        from_attributes = True  # Allows ORM model → Pydantic conversion


# ─────────────────────────────────────────────
# PRODUCT SCHEMAS
# ─────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, example="Industrial Drill Bit")
    sku: str = Field(..., min_length=1, max_length=100, example="DRILL-001")
    unit_price: float = Field(..., gt=0, example=29.99)
    stock_level: int = Field(default=0, ge=0, example=150)


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    unit_price: float
    stock_level: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# PURCHASE ORDER ITEM SCHEMAS
# ─────────────────────────────────────────────

class POItemCreate(BaseModel):
    product_id: int = Field(..., example=1)
    quantity: int = Field(..., gt=0, example=10)


class POItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float  # Snapshot price at order time
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# PURCHASE ORDER SCHEMAS
# ─────────────────────────────────────────────

class PurchaseOrderCreate(BaseModel):
    vendor_id: int = Field(..., example=1)
    items: List[POItemCreate] = Field(..., min_items=1)

    @validator("items")
    def items_not_empty(cls, v):
        if not v:
            raise ValueError("Purchase order must have at least one item.")
        return v


class PurchaseOrderResponse(BaseModel):
    id: int
    reference_no: str
    vendor_id: int
    total_amount: float
    status: POStatus
    created_at: datetime
    vendor: Optional[VendorResponse] = None
    items: Optional[List[POItemResponse]] = []

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# AI DESCRIPTION SCHEMA
# ─────────────────────────────────────────────

class AIDescriptionRequest(BaseModel):
    product_name: str
    category: Optional[str] = "General"


class AIDescriptionResponse(BaseModel):
    description: str
