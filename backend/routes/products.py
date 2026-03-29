"""
routes/products.py - API endpoints for Product management.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.schemas import ProductCreate, ProductResponse, AIDescriptionRequest, AIDescriptionResponse
from services import product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.
    - sku must be unique
    - unit_price must be > 0
    - stock_level defaults to 0
    """
    return product_service.create_product(db, product)


@router.get("/", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    """Return all products."""
    return product_service.get_all_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID."""
    return product_service.get_product_by_id(db, product_id)


@router.post("/ai-description", response_model=AIDescriptionResponse)
def generate_ai_description(request: AIDescriptionRequest):
    """
    Generate an AI-powered product description.
    Uses the Anthropic Claude API to produce a 2-sentence marketing description.
    Falls back to a template if API is unavailable.
    """
    import os, requests

    product_name = request.product_name
    category = request.category or "General"

    # Try calling the Claude API
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if api_key:
        try:
            prompt = (
                f"Write exactly 2 professional marketing sentences describing a product called "
                f"'{product_name}' in the '{category}' category. "
                f"Make it compelling, concise, and highlight its key value. "
                f"Output only the 2 sentences, nothing else."
            )
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 150,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                description = data["content"][0]["text"].strip()
                return AIDescriptionResponse(description=description)
        except Exception:
            pass  # Fall through to mock response

    # Mock fallback: deterministic template-based response
    description = (
        f"The {product_name} is a premium-grade {category.lower()} solution "
        f"engineered for reliability and peak performance. "
        f"Trusted by industry leaders, it delivers unmatched quality "
        f"and outstanding value for demanding professional environments."
    )
    return AIDescriptionResponse(description=description)
