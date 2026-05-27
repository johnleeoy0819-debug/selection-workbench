"""
评分引擎测试
验证五维评分计算
"""

import pytest
from services.scoring_engine import ScoringEngine


class TestScoringEngine:
    """测试评分引擎"""

    def test_composite_score_calculation(self):
        """测试综合评分计算"""
        engine = ScoringEngine()
        
        result = engine.calculate_score(
            demand_score=8,    # 8/10
            profit_score=7,    # 7/10
            competition_score=6,  # 6/10
            seasonal_score=5   # 5/10
        )
        
        # 综合分 = 8*0.35 + 7*0.30 + 6*0.25 + 5*0.10
        #        = 2.8 + 2.1 + 1.5 + 0.5
        #        = 6.9 → 69 分
        assert result.composite_score == 69

    def test_decision_execute(self):
        """测试立即执行决策"""
        engine = ScoringEngine()
        
        result = engine.calculate_score(
            demand_score=9,
            profit_score=8,
            competition_score=8,
            seasonal_score=7
        )
        
        # 综合分 = 9*0.35 + 8*0.30 + 8*0.25 + 7*0.10 = 8.35 → 83.5 → 82-84
        assert result.composite_score in [82, 83, 84]
        assert result.decision == "execute"
        assert result.confidence == "high"

    def test_decision_observe(self):
        """测试观察测试决策"""
        engine = ScoringEngine()
        
        result = engine.calculate_score(
            demand_score=6,
            profit_score=7,
            competition_score=6,
            seasonal_score=5
        )
        
        # 综合分 = 6*0.35 + 7*0.30 + 6*0.25 + 5*0.10 = 6.2 → 62
        assert result.composite_score in [61, 62]
        assert result.decision == "observe"
        assert result.confidence == "medium"

    def test_decision_abandon(self):
        """测试放弃决策"""
        engine = ScoringEngine()
        
        result = engine.calculate_score(
            demand_score=4,
            profit_score=3,
            competition_score=5,
            seasonal_score=2
        )
        
        # 综合分 = 4*0.35 + 3*0.30 + 5*0.25 + 2*0.10 = 3.55 → 35.5 → 35 or 36
        assert result.composite_score in [35, 36, 37]
        assert result.decision == "abandon"
        assert result.confidence == "high"

    def test_score_breakdown(self):
        """测试评分明细"""
        engine = ScoringEngine()
        
        result = engine.calculate_score(
            demand_score=8,
            profit_score=7,
            competition_score=6,
            seasonal_score=5
        )
        
        breakdown = result.breakdown
        assert breakdown["demand"].score == 8
        assert breakdown["demand"].weight == 0.35
        assert breakdown["demand"].weighted_score == 2.8
        
        assert breakdown["profit"].score == 7
        assert breakdown["profit"].weight == 0.30
        
        assert breakdown["competition"].score == 6
        assert breakdown["competition"].weight == 0.25
        
        assert breakdown["seasonal"].score == 5
        assert breakdown["seasonal"].weight == 0.10

    def test_custom_weights(self):
        """测试自定义权重"""
        engine = ScoringEngine(weights={
            "demand": 0.40,
            "profit": 0.30,
            "competition": 0.20,
            "seasonal": 0.10
        })
        
        result = engine.calculate_score(
            demand_score=8,
            profit_score=7,
            competition_score=6,
            seasonal_score=5
        )
        
        # 综合分 = 8*0.40 + 7*0.30 + 6*0.20 + 5*0.10 = 7.1 → 70 or 71
        assert result.composite_score in [70, 71]

    def test_invalid_score_range(self):
        """测试无效评分范围"""
        engine = ScoringEngine()
        
        with pytest.raises(ValueError):
            engine.calculate_score(
                demand_score=11,  # > 10
                profit_score=7,
                competition_score=6,
                seasonal_score=5
            )

    def test_invalid_weights_sum(self):
        """测试权重和不等于 1"""
        with pytest.raises(ValueError):
            ScoringEngine(weights={
                "demand": 0.50,
                "profit": 0.30,
                "competition": 0.20,
                "seasonal": 0.10  # 总和 1.10
            })
