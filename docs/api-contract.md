# API 契约 v0.1

> 前后端通信规范。前端只调这些接口，后端只返回这些格式。

**Base URL:** `http://18.234.173.5:8000`

---

## 1. 产品列表

```
GET /api/products?sort=score&order=desc&limit=20&offset=0
```

**Response 200:**
```json
{
  "total": 42,
  "products": [
    {
      "id": "prod_001",
      "name": "极简铁艺挂钩 3 钩款",
      "thumbnail": "/static/thumbnails/prod_001.jpg",
      "score": 89,
      "score_label": "高潜力",
      "price_etsy": 14.99,
      "cost_1688": 12.5,
      "margin_pct": 62,
      "keyword": "minimalist wall hook",
      "search_volume": 14800,
      "competition": "中",
      "compliance": "通过",
      "created_at": "2026-05-20T10:30:00Z"
    }
  ]
}
```

---

## 2. 单品详情

```
GET /api/products/:id
```

**Response 200:**
```json
{
  "id": "prod_001",
  "name": "极简铁艺挂钩 3 钩款",
  "images": ["/static/products/prod_001_01.jpg", "/static/products/prod_001_02.jpg"],
  "score": 89,
  "score_breakdown": {
    "market_opportunity": 92,
    "profit_margin": 85,
    "competition": 78,
    "compliance": 95,
    "procurement_ease": 88
  },
  "pricing": {
    "cost_1688": 12.5,
    "shipping": 25.0,
    "etsy_fee": 2.25,
    "listing_price": 14.99,
    "net_profit": 8.74,
    "margin_pct": 62
  },
  "keywords": [
    {"keyword": "minimalist wall hook", "volume": 14800, "competition": "中"},
    {"keyword": "modern coat hook", "volume": 6300, "competition": "中"},
    {"keyword": "black metal hook", "volume": 8900, "competition": "高"}
  ],
  "compliance": {
    "design_participation": "通过",
    "production_partner_disclosed": "通过",
    "not_simple_resale": "通过",
    "material_safety": "待确认",
    "notes": "需确认铁艺表面处理是否含铅"
  },
  "source_1688": {
    "url": "https://detail.1688.com/...",
    "supplier": "义乌XX五金厂",
    "moq": 50,
    "lead_time_days": 7
  }
}
```

---

## 3. 导入 eRank CSV

```
POST /api/products/import
Content-Type: multipart/form-data
Body: file=<CSV 文件>
```

**Response 200:**
```json
{
  "imported": 45,
  "skipped": 3,
  "errors": ["第 12 行: 缺少价格字段", "第 28 行: 关键词为空"],
  "new_products": ["prod_101", "prod_102", ...]
}
```

---

## 4. 关键词分析

```
GET /api/keywords?category=hook&sort=opportunity&limit=20
```

**Response 200:**
```json
{
  "category": "hook",
  "total_keywords": 128,
  "keywords": [
    {
      "keyword": "brass geometric hook",
      "search_volume": 4600,
      "competition_count": 890,
      "competition_level": "低",
      "opportunity_score": 92,
      "trend": "上升",
      "avg_price": 18.50
    }
  ]
}
```

---

## 5. 合规检查

```
GET /api/compliance/:id
```

**Response 200:**
```json
{
  "product_id": "prod_001",
  "checks": [
    {"item": "设计参与度", "status": "通过", "detail": "定制尺寸+颜色，非公模"},
    {"item": "生产商公开", "status": "通过", "detail": "已在 listing 公开"},
    {"item": "非简单转售", "status": "通过", "detail": "组合设计，非单品转售"},
    {"item": "材质安全", "status": "待确认", "detail": "需提供铅含量检测报告"}
  ],
  "overall": "3/4 通过"
}
```

---

## 6. 评分明细

```
GET /api/scoring/:id
```

**Response 200:**
```json
{
  "product_id": "prod_001",
  "total_score": 89,
  "dimensions": [
    {"name": "市场机会", "score": 92, "weight": 0.30, "reason": "月搜索量 14.8K，趋势上升"},
    {"name": "利润空间", "score": 85, "weight": 0.25, "reason": "毛利率 62%，净利 $8.74"},
    {"name": "竞争度",   "score": 78, "weight": 0.20, "reason": "竞品 3.2K，中等竞争"},
    {"name": "合规性",   "score": 95, "weight": 0.15, "reason": "3/4 项通过"},
    {"name": "采购便利", "score": 88, "weight": 0.10, "reason": "MOQ 50，7 天交货"}
  ]
}
```

---

## 错误响应格式

所有错误统一返回：

```json
{
  "error": true,
  "message": "产品不存在",
  "code": "NOT_FOUND"
}
```

**HTTP 状态码使用：**
- 200: 成功
- 201: 创建成功
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误
