"""
Pydantic 模型
请求/响应数据验证
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# ── 关键词 ──

class KeywordCreate(BaseModel):
    keyword: str
    avg_searches: Optional[int] = 0
    avg_clicks: Optional[int] = 0
    ctr: Optional[int] = 0
    competition: Optional[int] = 0
    kd: Optional[int] = 0


class KeywordResponse(KeywordCreate):
    id: int
    is_selected: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# ── 产品 ──

class ProductCreate(BaseModel):
    name: str
    keyword_id: Optional[int] = None
    subcategory: Optional[str] = None
    market_scope: Optional[str] = "us"
    source_type: Optional[str] = "manual"


class ProductResponse(ProductCreate):
    id: int
    product_id: Optional[str] = None
    status: str = "pending_analysis"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── 评分 ──

class ScoreCreate(BaseModel):
    demand_score: int = Field(..., ge=1, le=10)
    profit_score: int = Field(..., ge=1, le=10)
    competition_score: int = Field(..., ge=1, le=10)
    seasonal_score: int = Field(..., ge=1, le=10)


class ScoreResponse(BaseModel):
    composite_score: int
    decision: str
    confidence: str
    breakdown: dict


# ── 定价 ──

class PricingInput(BaseModel):
    unit_cost_cny: float
    shipping_cny: float
    custom_cny: float = 0
    packaging_usd: float = 0.8
    listing_price: float
    annual_revenue: float = 0


class PricingResponse(BaseModel):
    cog: float
    platform_fees: float
    net_profit: float
    net_margin_pct: float


# ── CSV 导入 ──

class ImportResponse(BaseModel):
    imported: int
    skipped: int
    errors: List[str]


# ── 通用 ──

class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    code: str
