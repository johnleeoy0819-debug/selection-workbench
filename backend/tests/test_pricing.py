"""
定价计算模块测试
验证成本、平台费、利润计算
"""

import pytest
from services.pricing_calculator import PricingCalculator


class TestPricingCalculator:
    """测试定价计算器"""

    def test_basic_cog_calculation(self):
        """测试基础 COG 计算"""
        calc = PricingCalculator(exchange_rate=7.0)
        
        result = calc.calculate_cog(
            unit_cost_cny=12.5,
            shipping_cny=8.0,
            custom_cny=0,
            packaging_usd=0.8
        )
        
        # (12.5 + 8.0) / 7.0 + 0.8 = 2.93 + 0.8 = 3.73
        assert result == pytest.approx(3.73, rel=0.01)

    def test_cog_with_custom_fee(self):
        """测试含定制费的 COG"""
        calc = PricingCalculator(exchange_rate=7.0)
        
        result = calc.calculate_cog(
            unit_cost_cny=15.0,
            shipping_cny=10.0,
            custom_cny=5.0,
            packaging_usd=0.8
        )
        
        # (15 + 10 + 5) / 7 + 0.8 = 4.29 + 0.8 = 5.09
        assert result == pytest.approx(5.09, rel=0.01)

    def test_platform_fees_without_offsite_ads(self):
        """测试无站外广告的平��费"""
        calc = PricingCalculator(exchange_rate=7.0)
        
        fees = calc.calculate_platform_fees(
            listing_price=14.99,
            annual_revenue=5000  # < $10K
        )
        
        # Listing: $0.20
        # Transaction: 14.99 * 6.5% = 0.97
        # Payment: 14.99 * 3.5% = 0.52
        # Offsite Ads: 0
        expected = 0.20 + 0.97 + 0.52
        assert fees == pytest.approx(expected, rel=0.01)

    def test_platform_fees_with_offsite_ads(self):
        """测试有站外广告的平台费"""
        calc = PricingCalculator(exchange_rate=7.0)
        
        fees = calc.calculate_platform_fees(
            listing_price=14.99,
            annual_revenue=15000  # > $10K
        )
        
        # Listing: $0.20
        # Transaction: 14.99 * 6.5% = 0.97
        # Payment: 14.99 * 3.5% = 0.52
        # Offsite Ads: 14.99 * 15% = 2.25
        expected = 0.20 + 0.97 + 0.52 + 2.25
        assert fees == pytest.approx(expected, rel=0.01)

    def test_profit_calculation(self):
        """测试利润计算"""
        calc = PricingCalculator(exchange_rate=7.0)
        
        result = calc.calculate_profit(
            listing_price=14.99,
            cog=3.73,
            annual_revenue=5000
        )
        
        # 平台费 = 0.20 + 0.97 + 0.52 = 1.69
        # 净利润 = 14.99 - 3.73 - 1.69 = 9.57
        # 净利率 = 9.57 / 14.99 = 63.8%
        assert result["net_profit"] == pytest.approx(9.57, rel=0.01)
        assert result["net_margin_pct"] == pytest.approx(63.8, rel=0.1)

    def test_full_pricing_breakdown(self):
        """测试完整定价明细"""
        calc = PricingCalculator(exchange_rate=7.0)
        
        result = calc.get_pricing_breakdown(
            unit_cost_cny=12.5,
            shipping_cny=8.0,
            custom_cny=0,
            packaging_usd=0.8,
            listing_price=14.99,
            annual_revenue=5000
        )
        
        assert result.cog == pytest.approx(3.73, rel=0.01)
        assert result.platform_fees == pytest.approx(1.69, rel=0.01)
        assert result.net_profit == pytest.approx(9.57, rel=0.01)
        assert result.net_margin_pct == pytest.approx(63.8, rel=0.1)

    def test_different_exchange_rates(self):
        """测试不同汇率"""
        calc = PricingCalculator(exchange_rate=7.2)
        
        result = calc.calculate_cog(
            unit_cost_cny=12.5,
            shipping_cny=8.0,
            custom_cny=0,
            packaging_usd=0.8
        )
        
        # (12.5 + 8.0) / 7.2 + 0.8 = 2.85 + 0.8 = 3.65
        assert result == pytest.approx(3.65, rel=0.01)
