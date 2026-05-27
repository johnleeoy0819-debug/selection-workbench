"""
关键词 API
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import io

from database.connection import get_db
from database.models import Keyword
from models.schemas import KeywordResponse, ImportResponse
from services.csv_importer import CSVImporter

router = APIRouter(prefix="/api/keywords", tags=["keywords"])


@router.post("/import", response_model=ImportResponse)
async def import_keywords(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    导入 eRank CSV 文件
    
    支持两种格式：
    - 关键词列表（Keyword List）
    - Top Listings
    """
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(400, "只支持 CSV 文件")
    
    # 文件大小限制 10MB
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "文件大小超过 10MB 限制")
    file_obj = io.StringIO(content.decode('utf-8-sig'))
    
    importer = CSVImporter()
    
    try:
        result = importer.parse(file_obj)
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    # 保存到数据库
    for kw_data in result.keywords:
        existing = db.query(Keyword).filter(
            Keyword.keyword == kw_data["keyword"]
        ).first()
        
        if existing:
            result.skipped += 1
            continue
        
        keyword = Keyword(**kw_data)
        db.add(keyword)
        result.imported += 1
    
    db.commit()
    
    return ImportResponse(
        imported=result.imported,
        skipped=result.skipped,
        errors=result.errors
    )


@router.get("", response_model=List[KeywordResponse])
def get_keywords(
    skip: int = 0,
    limit: int = 100,
    sort: str = "avg_searches",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    """获取关键词列表"""
    query = db.query(Keyword)
    
    # 排序
    if hasattr(Keyword, sort):
        sort_col = getattr(Keyword, sort)
        if order == "desc":
            sort_col = sort_col.desc()
        query = query.order_by(sort_col)
    
    keywords = query.offset(skip).limit(limit).all()
    return keywords


@router.get("/{keyword_id}", response_model=KeywordResponse)
def get_keyword(keyword_id: int, db: Session = Depends(get_db)):
    """获取单个关键词"""
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(404, "关键词不存在")
    return keyword


@router.put("/{keyword_id}/select")
def toggle_keyword_select(keyword_id: int, db: Session = Depends(get_db)):
    """切换关键词选中状态"""
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(404, "关键词不存在")
    
    keyword.is_selected = not keyword.is_selected
    db.commit()
    
    return {"id": keyword_id, "is_selected": keyword.is_selected}
