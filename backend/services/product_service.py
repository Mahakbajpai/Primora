from sqlalchemy.orm import Session
from models.models import Product
from schemas.schemas import ProductCreate
from fastapi import HTTPException

def create_product(db: Session, product_data: ProductCreate) -> Product:
    try:
        existing = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Product with SKU '{product_data.sku}' already exists.")
        product = Product(name=product_data.name, sku=product_data.sku, unit_price=product_data.unit_price, stock_level=product_data.stock_level)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

def get_all_products(db: Session) -> list:
    try:
        return db.query(Product).order_by(Product.name).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")

def get_product_by_id(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
    return product

def update_product_description(db: Session, product_id: int, description: str) -> Product:
    product = get_product_by_id(db, product_id)
    try:
        product.description = description
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update description: {str(e)}")
