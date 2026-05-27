"""
定价计算 API
"""

from fastapi import APIRouter
from models.schemas import PricingInput, PricingResponse
from services.pricing_calculator import PricingCalculator

router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@router.post("/calculate", response_model=PricingResponse)
def calculate_pricing(input_data: PricingInput):
    """
    计算定价明细
    
    输入：成本数据 + 售价
    输出：COG / 平台费 / 净利润 / 净利率
    """
    calc = PricingCalculator()
    
    result = calc.get_pricing_breakdown(
        unit_cost_cny=input_data.unit_cost_cny,
        shipping_cny=input_data.shipping_cny,
        custom_cny=input_data.custom_cny,
        packaging_usd=input_data.packaging_usd,
        listing_price=input_data.listing_price,
        annual_revenue=input_data.annual_revenue
    )
    
    return PricingResponse(
        cog=result.cog,
        platform_fees=result.platform_fees,
        net_profit=result.net_profit,
        net_margin_pct=result.net_margin_pct
    )
