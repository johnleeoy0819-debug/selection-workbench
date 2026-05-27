"""
产品 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from database.models import Product
from models.schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/api/products", tags=["products"])


@router.post("", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """创建产品"""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取产品列表"""
    query = db.query(Product)
    if status:
        query = query.filter(Product.status == status)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取单个产品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "产品不存在")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductCreate,
    db: Session = Depends(get_db)
):
    """更新产品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "产品不存在")
    
    for key, value in product_update.model_dump().items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """删除产品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "产品不存在")
    
    db.delete(product)
    db.commit()
    return {"message": "已删除"}
