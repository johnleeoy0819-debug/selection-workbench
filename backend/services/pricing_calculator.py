"""
定价计算服务
计算 COG、平台费、净利润
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class PricingBreakdown:
    """定价明细"""
    cog: float
    platform_fees: float
    net_profit: float
    net_margin_pct: float


class PricingCalculator:
    """定价计算器"""
    
    # Etsy 费用常量
    LISTING_FEE = 0.20
    TRANSACTION_FEE_PCT = 0.065
    PAYMENT_FEE_PCT = 0.035
    OFFSITE_ADS_FEE_PCT = 0.15
    OFFSITE_ADS_THRESHOLD = 10000
    
    def __init__(self, exchange_rate: float = 7.0):
        """
        初始化计算器
        
        Args:
            exchange_rate: CNY/USD 汇率
        """
        self.exchange_rate = exchange_rate
    
    def calculate_cog(
        self,
        unit_cost_cny: float,
        shipping_cny: float,
        custom_cny: float = 0,
        packaging_usd: float = 0.8
    ) -> float:
        """
        计算商品总成本 (COG)
        
        Args:
            unit_cost_cny: 单价（人民币）
            shipping_cny: 运费（人民币）
            custom_cny: 定制费（人民币）
            packaging_usd: 包装费（美元）
            
        Returns:
            COG（美元）
        """
        cny_total = unit_cost_cny + shipping_cny + custom_cny
        usd_total = cny_total / self.exchange_rate
        return usd_total + packaging_usd
    
    def calculate_platform_fees(
        self,
        listing_price: float,
        annual_revenue: float = 0
    ) -> float:
        """
        计算 Etsy 平台费
        
        Args:
            listing_price: 售价
            annual_revenue: 年销售额（用于判断 Offsite Ads）
            
        Returns:
            平台费总额
        """
        listing_fee = self.LISTING_FEE
        transaction_fee = listing_price * self.TRANSACTION_FEE_PCT
        payment_fee = listing_price * self.PAYMENT_FEE_PCT
        
        # Offsite Ads：年销售额 >= $10K 时强制 15%
        offsite_ads_fee = 0.0
        if annual_revenue >= self.OFFSITE_ADS_THRESHOLD:
            offsite_ads_fee = listing_price * self.OFFSITE_ADS_FEE_PCT
        
        return listing_fee + transaction_fee + payment_fee + offsite_ads_fee
    
    def calculate_profit(
        self,
        listing_price: float,
        cog: float,
        annual_revenue: float = 0
    ) -> Dict[str, float]:
        """
        计算利润
        
        Args:
            listing_price: 售价
            cog: 商品总成本
            annual_revenue: 年销售额
            
        Returns:
            {"net_profit": 净利润, "net_margin_pct": 净利率}
        """
        platform_fees = self.calculate_platform_fees(listing_price, annual_revenue)
        net_profit = listing_price - cog - platform_fees
        net_margin_pct = (net_profit / listing_price * 100) if listing_price > 0 else 0
        
        return {
            "net_profit": round(net_profit, 2),
            "net_margin_pct": round(net_margin_pct, 1)
        }
    
    def get_pricing_breakdown(
        self,
        unit_cost_cny: float,
        shipping_cny: float,
        custom_cny: float = 0,
        packaging_usd: float = 0.8,
        listing_price: float = 0,
        annual_revenue: float = 0
    ) -> PricingBreakdown:
        """
        获取完整定价明细
        
        Args:
            unit_cost_cny: 单价（人民币）
            shipping_cny: 运费（人民币）
            custom_cny: 定制费（人民币）
            packaging_usd: 包装费（美元）
            listing_price: 售价
            annual_revenue: 年销售额
            
        Returns:
            PricingBreakdown 定价明细
        """
        cog = self.calculate_cog(unit_cost_cny, shipping_cny, custom_cny, packaging_usd)
        platform_fees = self.calculate_platform_fees(listing_price, annual_revenue)
        profit_result = self.calculate_profit(listing_price, cog, annual_revenue)
        
        return PricingBreakdown(
            cog=round(cog, 2),
            platform_fees=round(platform_fees, 2),
            net_profit=profit_result["net_profit"],
            net_margin_pct=profit_result["net_margin_pct"]
        )
