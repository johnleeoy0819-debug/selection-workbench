"""
AI 智能评分服务 - DeepSeek v4 pro
基于关键词数据生成五维评分和决策建议
"""

import os
import json
from typing import Optional
import httpx

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = "deepseek-v4-pro"


async def ai_score_keyword(
    keyword: str,
    avg_searches: Optional[int] = None,
    avg_clicks: Optional[int] = None,
    ctr: Optional[int] = None,
    competition: Optional[int] = None,
    kd: Optional[int] = None,
    peak_months: Optional[str] = None,
) -> dict:
    """
    调用 DeepSeek API 对关键词进行智能评分
    
    Returns:
        {
            "demand_score": 1-10,
            "profit_score": 1-10, 
            "competition_score": 1-10,
            "seasonal_score": 1-10,
            "composite_score": 0-100,
            "decision": "execute|observe|abandon",
            "reasoning": "分析理由..."
        }
    """
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY not configured")
    
    prompt = _build_scoring_prompt(
        keyword=keyword,
        avg_searches=avg_searches,
        avg_clicks=avg_clicks,
        ctr=ctr,
        competition=competition,
        kd=kd,
        peak_months=peak_months,
    )
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": _SCORING_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        data = resp.json()
        
    content = data["choices"][0]["message"]["content"]
    result = json.loads(content)
    
    # 验证并规范化返回
    return _normalize_result(result)


_SCORING_SYSTEM_PROMPT = """你是 Maple Hollow Home 的 AI 选品分析师，专注于 Etsy 平台 Home & Living 类目（Desk Decor + Wall Decor）。

请根据提供的关键词数据，从以下五个维度进行评分（1-10分），并给出综合评分和决策建议。

评分维度：
1. demand_score（需求强度，权重35%）：基于搜索量、点击量判断买家需求
2. profit_score（利润潜力，权重30%）：基于竞争度、KD值判断定价空间和利润空间  
3. competition_score（竞争格局，权重25%）：基于竞争度、CTR判断进入难度
4. seasonal_score（节日/季节性，权重10%）：基于peak_months判断时效性和节日潜力

决策规则：
- execute（执行）：composite_score >= 70，需求明确、利润可观、竞争可控
- observe（观察）：composite_score 50-69，有潜力但需进一步验证
- abandon（放弃）：composite_score < 50，需求不足或竞争过于激烈

输出格式必须是 JSON：
{
    "demand_score": int,
    "profit_score": int,
    "competition_score": int,
    "seasonal_score": int,
    "composite_score": int,
    "decision": "execute|observe|abandon",
    "reasoning": "详细分析理由，包括数据解读和风险提示"
}

注意：
- 评分要基于实际数据，不要臆测
- 对于 Home & Living 类目，$15-60 价格带是核心区间
- 轻定制（engraving/color/dates）是加分项
- 美国市场是主要目标"""


def _build_scoring_prompt(
    keyword: str,
    avg_searches: Optional[int] = None,
    avg_clicks: Optional[int] = None,
    ctr: Optional[int] = None,
    competition: Optional[int] = None,
    kd: Optional[int] = None,
    peak_months: Optional[str] = None,
) -> str:
    """构建评分提示词"""
    lines = [f"关键词: {keyword}"]
    
    if avg_searches is not None:
        lines.append(f"月均搜索量: {avg_searches}")
    if avg_clicks is not None:
        lines.append(f"月均点击量: {avg_clicks}")
    if ctr is not None:
        lines.append(f"CTR: {ctr}%")
    if competition is not None:
        lines.append(f"竞争度: {competition}/100")
    if kd is not None:
        lines.append(f"KD值: {kd}/100")
    if peak_months:
        lines.append(f"高峰月份: {peak_months}")
    
    lines.append("\n请基于以上数据进行五维评分，并给出决策建议。")
    return "\n".join(lines)


def _normalize_result(result: dict) -> dict:
    """规范化 AI 返回结果"""
    normalized = {
        "demand_score": _clamp(int(result.get("demand_score", 5)), 1, 10),
        "profit_score": _clamp(int(result.get("profit_score", 5)), 1, 10),
        "competition_score": _clamp(int(result.get("competition_score", 5)), 1, 10),
        "seasonal_score": _clamp(int(result.get("seasonal_score", 5)), 1, 10),
        "composite_score": _clamp(int(result.get("composite_score", 50)), 0, 100),
        "decision": result.get("decision", "observe"),
        "reasoning": result.get("reasoning", ""),
    }
    
    # 验证 decision 合法性
    if normalized["decision"] not in ("execute", "observe", "abandon"):
        normalized["decision"] = "observe"
    
    return normalized


def _clamp(value: int, min_val: int, max_val: int) -> int:
    """限制数值范围"""
    return max(min_val, min(max_val, value))
