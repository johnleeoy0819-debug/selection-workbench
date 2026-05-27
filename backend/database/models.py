"""
SQLAlchemy ORM 模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database.connection import Base


class Keyword(Base):
    """关键词表"""
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String, nullable=False, unique=True)
    avg_searches = Column(Integer)
    avg_clicks = Column(Integer)
    ctr = Column(Integer)
    competition = Column(Integer)
    kd = Column(Integer)
    tag_occurrences = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    google_searches = Column(Integer, default=0)
    peak_months = Column(String)
    time_status = Column(String)
    gift_potential = Column(String)
    is_selected = Column(Boolean, default=False)
    source = Column(String, default="erank")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    listings = relationship("CompetitorListing", back_populates="keyword")
    products = relationship("Product", back_populates="keyword")


class CompetitorListing(Base):
    """竞品 Listing 表"""
    __tablename__ = "competitor_listings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"))
    title = Column(String, nullable=False)
    age_days = Column(Integer)
    views = Column(Integer)
    daily_views = Column(Integer)
    est_sales = Column(Integer)
    price = Column(Float)
    est_revenue = Column(Float)
    hearts = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    keyword = relationship("Keyword", back_populates="listings")


class Product(Base):
    """产品表"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, unique=True)
    name = Column(String, nullable=False)
    keyword_id = Column(Integer, ForeignKey("keywords.id"))
    subcategory = Column(String)
    market_scope = Column(String)
    status = Column(String, default="pending_analysis")
    source_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    keyword = relationship("Keyword", back_populates="products")
    scores = relationship("ProductScore", back_populates="product")


class ProductScore(Base):
    """评分明细表"""
    __tablename__ = "product_scores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    demand_score = Column(Integer)
    profit_score = Column(Integer)
    competition_score = Column(Integer)
    seasonal_score = Column(Integer)
    compliance_score = Column(Integer)
    composite_score = Column(Integer)
    final_decision = Column(String)
    confidence_level = Column(String)
    scoring_version = Column(String, default="v1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="scores")


class Config(Base):
    """系统配置表"""
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True)
    exchange_rate = Column(Float, default=7.0)
    exchange_rate_last_updated = Column(DateTime)
    offsite_ads_threshold = Column(Float, default=10000)
    annual_revenue = Column(Float, default=0)
    scoring_version = Column(String, default="v1.0")
