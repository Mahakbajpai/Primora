"""
routes/vendors.py - API endpoints for Vendor management.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas.schemas import VendorCreate, VendorResponse
from services import vendor_service

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/", response_model=VendorResponse, status_code=201)
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    """
    Create a new vendor.
    - name: Vendor company name
    - contact: Email or phone
    - rating: 0.0 to 5.0
    """
    return vendor_service.create_vendor(db, vendor)


@router.get("/", response_model=List[VendorResponse])
def list_vendors(
    search: Optional[str] = Query(None, description="Search vendors by name or contact"),
    db: Session = Depends(get_db)
):
    """
    List all vendors. Optionally filter by name/contact with ?search=keyword
    """
    return vendor_service.get_all_vendors(db, search=search)


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Get a single vendor by ID."""
    return vendor_service.get_vendor_by_id(db, vendor_id)
