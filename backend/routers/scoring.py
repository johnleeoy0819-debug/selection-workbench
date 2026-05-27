"""
评分 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Product, ProductScore
from models.schemas import ScoreCreate, ScoreResponse
from services.scoring_engine import ScoringEngine
from services.pricing_calculator import PricingCalculator

from services.ai_scoring import ai_score_keyword

router = APIRouter(prefix="/api/scoring", tags=["scoring"])


@router.post("/ai/{keyword_id}")
async def ai_score_keyword_endpoint(
    keyword_id: int,
    db: Session = Depends(get_db)
):
    """
    AI 智能评分 - 基于关键词数据调用 DeepSeek v4 pro
    
    输入：keyword_id
    输出：五维评分 + 决策建议 + AI 分析理由
    """
    from database.models import Keyword
    
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(404, "关键词不存在")
    
    try:
        result = await ai_score_keyword(
            keyword=str(keyword.keyword),
            avg_searches=int(keyword.avg_searches) if keyword.avg_searches else None,
            avg_clicks=int(keyword.avg_clicks) if keyword.avg_clicks else None,
            ctr=int(keyword.ctr) if keyword.ctr else None,
            competition=int(keyword.competition) if keyword.competition else None,
            kd=int(keyword.kd) if keyword.kd else None,
            peak_months=str(keyword.peak_months) if keyword.peak_months else None,
        )
        return {
            "keyword": keyword.keyword,
            "ai_scores": result,
            "model": "deepseek-v4-pro"
        }
    except ValueError as e:
        raise HTTPException(500, f"AI 评分服务未配置: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"AI 评分失败: {str(e)}")


@router.post("/{product_id}", response_model=ScoreResponse)
def score_product(
    product_id: int,
    scores: ScoreCreate,
    db: Session = Depends(get_db)
):
    """
    为产品评分
    
    输入：五维评分（1-10）
    输出：综合评分 + 决策建议
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "产品不存在")
    
    # 计算评分
    engine = ScoringEngine()
    result = engine.calculate_score(
        demand_score=scores.demand_score,
        profit_score=scores.profit_score,
        competition_score=scores.competition_score,
        seasonal_score=scores.seasonal_score
    )
    
    # 保存到数据库
    db_score = ProductScore(
        product_id=product_id,
        demand_score=scores.demand_score,
        profit_score=scores.profit_score,
        competition_score=scores.competition_score,
        seasonal_score=scores.seasonal_score,
        composite_score=result.composite_score,
        final_decision=result.decision,
        confidence_level=result.confidence
    )
    db.add(db_score)
    db.commit()
    
    return ScoreResponse(
        composite_score=result.composite_score,
        decision=result.decision,
        confidence=result.confidence,
        breakdown={
            k: {
                "score": v.score,
                "weight": v.weight,
                "weighted_score": v.weighted_score
            }
            for k, v in result.breakdown.items()
        }
    )


@router.get("/{product_id}/history")
def get_score_history(product_id: int, db: Session = Depends(get_db)):
    """获取评分历史"""
    scores = db.query(ProductScore).filter(
        ProductScore.product_id == product_id
    ).order_by(ProductScore.created_at.desc()).all()
    
    return scores
