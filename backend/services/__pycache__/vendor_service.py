"""
services/vendor_service.py - Business logic for Vendor operations.
Keeps routes thin and logic testable.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.models.models import Vendor
from backend.schemas.schemas import VendorCreate
from fastapi import HTTPException


def create_vendor(db: Session, vendor_data: VendorCreate) -> Vendor:
    """Create a new vendor record."""
    try:
        vendor = Vendor(
            name=vendor_data.name,
            contact=vendor_data.contact,
            rating=vendor_data.rating
        )
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        return vendor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create vendor: {str(e)}")


def get_all_vendors(db: Session, search: str = None) -> list:
    """
    Return all vendors. Optional search filter on name or contact.
    Search is case-insensitive using ilike.
    """
    try:
        query = db.query(Vendor)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Vendor.name.ilike(pattern),
                    Vendor.contact.ilike(pattern)
                )
            )
        return query.order_by(Vendor.name).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vendors: {str(e)}")


def get_vendor_by_id(db: Session, vendor_id: int) -> Vendor:
    """Fetch a single vendor by PK. Raises 404 if not found."""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail=f"Vendor with id {vendor_id} not found.")
    return vendor
