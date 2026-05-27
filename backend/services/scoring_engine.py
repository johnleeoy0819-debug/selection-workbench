"""
评分引擎
五维评分：需求/利润/竞争/节日/合规
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ScoreBreakdown:
    """评分明细"""
    score: int
    weight: float
    weighted_score: float


@dataclass
class ScoringResult:
    """评分结果"""
    composite_score: int
    decision: str
    confidence: str
    breakdown: Dict[str, ScoreBreakdown]


class ScoringEngine:
    """评分引擎"""
    
    # 默认权重
    DEFAULT_WEIGHTS = {
        "demand": 0.35,
        "profit": 0.30,
        "competition": 0.25,
        "seasonal": 0.10
    }
    
    # 决策阈值
    DECISION_THRESHOLDS = {
        "execute": (80, 100),
        "observe": (60, 79),
        "abandon": (0, 59)
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        初始化评分引擎
        
        Args:
            weights: 自定义权重，默认 DEFAULT_WEIGHTS
            
        Raises:
            ValueError: 权重和不等于 1 或包含无效维度
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._validate_weights()
    
    def _validate_weights(self) -> None:
        """验证权重配置"""
        # 检查维度
        valid_dimensions = set(self.DEFAULT_WEIGHTS.keys())
        if set(self.weights.keys()) != valid_dimensions:
            raise ValueError(f"权重必须包含以下维度: {valid_dimensions}")
        
        # 检查和
        total = sum(self.weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"权重和必须等于 1，当前: {total}")
    
    def calculate_score(
        self,
        demand_score: int,
        profit_score: int,
        competition_score: int,
        seasonal_score: int
    ) -> ScoringResult:
        """
        计算综合评分
        
        Args:
            demand_score: 需求评分 (1-10)
            profit_score: 利润评分 (1-10)
            competition_score: 竞争评分 (1-10)
            seasonal_score: 节日评分 (1-10)
            
        Returns:
            ScoringResult 评分结果
            
        Raises:
            ValueError: 评分不在 1-10 范围内
        """
        scores = {
            "demand": demand_score,
            "profit": profit_score,
            "competition": competition_score,
            "seasonal": seasonal_score
        }
        
        # 验证评分范围
        for dimension, score in scores.items():
            if not (1 <= score <= 10):
                raise ValueError(f"{dimension} 评分必须在 1-10 之间，当前: {score}")
        
        # 计算加权分
        breakdown = {}
        weighted_total = 0.0
        
        for dimension, score in scores.items():
            weight = self.weights[dimension]
            weighted = score * weight
            weighted_total += weighted
            
            breakdown[dimension] = ScoreBreakdown(
                score=score,
                weight=weight,
                weighted_score=round(weighted, 2)
            )
        
        # 综合评分 (0-100)
        composite_score = int(weighted_total * 10)
        
        # 决策建议
        decision, confidence = self._get_decision(composite_score)
        
        return ScoringResult(
            composite_score=composite_score,
            decision=decision,
            confidence=confidence,
            breakdown=breakdown
        )
    
    def _get_decision(self, composite_score: int) -> tuple:
        """
        根据综合评分获取决策建议
        
        Args:
            composite_score: 综合评分 (0-100)
            
        Returns:
            (decision, confidence) 元组
        """
        if composite_score >= 80:
            return ("execute", "high")
        elif composite_score >= 60:
            return ("observe", "medium")
        else:
            return ("abandon", "high")
