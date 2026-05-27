# Maple Hollow AI Product Intelligence System — 工程规格书

> 版本：V3 整合版  
> 日期：2026-05-28  
> 状态：Production Ready（Phase 1）

---

## 一、系统定义

### 1.1 产品本质

不是工具，而是：

```
AI 驱动的选品决策系统（Product Intelligence System）
```

核心能力：

```
数据 → 洞察 → 产品 → 供应链 → 利润
```

### 1.2 商业目标

- 找到 **低竞争 + 高需求 + 可采购** 的产品
- 自动生成 1688 供应路径
- 降低选品失败率
- 提升单品利润率

### 1.3 系统输出

不是"关键词"，而是：

```
可执行产品机会（Product Opportunity）
```

结构：

```json
{
  "product": "desk organizer",
  "score": 84,
  "reason": "high demand + low competition + strong cottagecore trend",
  "supplier_path": "木质桌面收纳盒 / 实木办公收纳盒 / 胡桃木桌面整理盒",
  "estimated_margin": "62%"
}
```

---

## 二、技术架构

### 2.1 技术栈（现实约束版）

```yaml
Frontend:
  - React 19 + Vite 6
  - Vercel
  - 手写 CSS（minimalist-ui）

Backend:
  - FastAPI
  - Python 3.14

Database:
  - SQLite（Phase 1）
  - 预留 PostgreSQL 迁移路径

LLM:
  - DeepSeek v4 pro
  - 未来可切换 OpenAI / Claude

Infra:
  - EC2（data 盘）
  - systemd 守护进程
```

### 2.2 三层架构

```
Data Layer（Etsy / eRank / 1688 / 用户录入）
    ↓
Rule Engine（评分 / 排序 / 决策阈值）
    ↓
LLM Layer（特征提取 / 聚类 / 关键词生成）
    ↓
Human Decision Layer（确认 / 修正 / 最终决策）
```

### 2.3 核心原则

```
LLM 不做决策
LLM 不做评分
LLM 不做排序
LLM 只做结构化理解
```

---

## 三、数据库设计

### 3.1 核心表

```sql
-- 关键词主表
CREATE TABLE keyword_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    source TEXT DEFAULT 'erank',
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 关键词指标（来自 eRank Keyword Tool）
CREATE TABLE keyword_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER REFERENCES keyword_master(id),
    avg_searches INTEGER,
    avg_clicks INTEGER,
    ctr INTEGER,
    competition INTEGER,
    kd INTEGER,
    google_searches INTEGER DEFAULT 0,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Listing 数据（来自 eRank Top Listings）
CREATE TABLE listing_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER REFERENCES keyword_master(id),
    title TEXT NOT NULL,
    age_days INTEGER,
    views INTEGER,
    daily_views INTEGER,
    est_sales INTEGER,
    price REAL,
    est_revenue REAL,
    hearts INTEGER,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 证据链（关键升级）
CREATE TABLE analysis_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER REFERENCES keyword_master(id),
    evidence_type TEXT CHECK(evidence_type IN (
        'search_growth', 'ctr_above_avg', 'sales_validated',
        'low_competition', 'trend_up', 'brand_fit', 'margin_healthy'
    )),
    evidence_value TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 产品 DNA（系统核心资产）
CREATE TABLE product_dna (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER REFERENCES keyword_master(id),
    style TEXT,
    material TEXT,
    color TEXT,
    feature TEXT,
    customer TEXT,
    confidence INTEGER CHECK(confidence BETWEEN 0 AND 100),
    extracted_by TEXT DEFAULT 'deepseek-v4-pro',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 历史决策（学习引擎核心）
CREATE TABLE historical_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER REFERENCES keyword_master(id),
    predicted_score INTEGER,
    actual_profit REAL,
    actual_sales INTEGER,
    decision TEXT CHECK(decision IN ('execute', 'observe', 'abandon')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 供应商候选
CREATE TABLE supplier_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER REFERENCES keyword_master(id),
    supplier_name TEXT,
    supplier_url TEXT,
    unit_cost_cny REAL,
    moq INTEGER,
    repeat_rate REAL,
    oem BOOLEAN DEFAULT 0,
    years INTEGER,
    supplier_score INTEGER,
    source TEXT DEFAULT 'manual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 评分权重版本管理
CREATE TABLE scoring_weights (
    version TEXT PRIMARY KEY,
    demand_weight REAL DEFAULT 0.35,
    competition_weight REAL DEFAULT 0.25,
    margin_weight REAL DEFAULT 0.20,
    trend_weight REAL DEFAULT 0.15,
    brandfit_weight REAL DEFAULT 0.05,
    is_active BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 初始化数据

```sql
-- 默认评分权重
INSERT INTO scoring_weights (version, demand_weight, competition_weight, 
    margin_weight, trend_weight, brandfit_weight, is_active)
VALUES ('v1.0', 0.35, 0.25, 0.20, 0.15, 0.05, 1);
```

---

## 四、Agent 设计

### 4.1 Agent 清单

| Agent | 职责 | 输入 | 输出 | 执行者 |
|:---|:---|:---|:---|:---|
| **Category Agent** | 分析 CSV，发现机会类目 | 3类目×4表 CSV | 各类目评分简报 | 规则引擎 |
| **Keyword Agent** | 关键词扩展 + 聚类 | 种子关键词池 | 聚类结果 + 扩展词 | LLM |
| **Feature Agent** | 提取材质 / 风格 / 功能 | Top Listings | product_dna JSON | LLM |
| **Winning Pattern Agent** | 分析 Top Listing 成功模式 | Top 100 Listings | 成功模式 JSON | LLM |
| **Review Agent** | 间接分析需求（Phase 2） | Hearts / Sales / Views / Tags | 推断需求 JSON | LLM |
| **Supply Agent** | 生成 1688 关键词 | product_dna | 中文采购词 JSON | LLM |

### 4.2 Agent 边界

```
LLM 禁止：
- 推荐产品
- 排序产品
- 判断是否值得做
- 计算利润
- 输出解释性文字（只输出 JSON）

LLM 允许：
- 分类
- 归纳
- 提取
- 聚类
- 结构化输出
```

---

## 五、评分引擎（唯一决策层）

### 5.1 Opportunity Score

```python
Opportunity Score =
    Demand      * 0.35 +
    Competition * 0.25 +
    Margin      * 0.20 +
    Trend       * 0.15 +
    BrandFit    * 0.05
```

### 5.2 子评分计算

| 维度 | 指标 | 计算方式 |
|:---|:---|:---|
| **Demand** | 搜索量、点击量、CTR | `normalize(avg_searches) * 0.4 + normalize(avg_clicks) * 0.3 + normalize(ctr) * 0.3` |
| **Competition** | 竞争数、KD | `100 - (normalize(competition) * 0.6 + normalize(kd) * 0.4)` |
| **Margin** | 预估利润率 | 需要 1688 成本数据，`(售价 - 成本) / 售价 * 100` |
| **Trend** | Google Trends（Phase 2） | 暂时用规则替代：上升=10，持平=5，下降=0 |
| **BrandFit** | 关键词含目标风格 | farmhouse/cottagecore/rustic/minimalist/nature = 10，其他 = 0-5 |

### 5.3 决策阈值

| 分数 | 等级 | 行动 |
|:---|:---|:---|
| 90+ | **Strong Buy** | 立即进入 Keyword Tool 深入分析 |
| 80-90 | **Worth Research** | 进入观察池，进一步验证 |
| 70-80 | **Watch List** | 月度复查，等待信号 |
| <70 | **Ignore** | 过滤掉 |

### 5.4 原则

```
LLM 不能影响评分
评分完全由规则引擎计算
权重版本化管理，支持历史对比
```

---

## 六、Prompt 工程化规范

### 6.1 全局 System Prompt

```text
你是结构化电商分析系统。

规则：
- 不允许推荐产品
- 不允许排序产品
- 不允许判断是否值得做
- 不允许输出解释性文字
- 只能输出 JSON
- 字段缺失时返回 null
- 置信度必须 0-100 整数
```

### 6.2 Feature Extraction Prompt

**Input Schema：**

```json
{
  "keyword": "desk organizer",
  "sample_size": 50,
  "listings": [
    {
      "title": "Wood Desk Organizer with Drawer",
      "views": 12000,
      "sales": 800,
      "price": 29.99,
      "hearts": 450
    }
  ]
}
```

**Output Schema：**

```json
{
  "materials": [
    {"name": "wood", "confidence": 92},
    {"name": "bamboo", "confidence": 45}
  ],
  "styles": [
    {"name": "rustic", "confidence": 78},
    {"name": "minimalist", "confidence": 65}
  ],
  "features": [
    {"name": "drawer", "confidence": 88},
    {"name": "phone_holder", "confidence": 52}
  ],
  "colors": [
    {"name": "natural_wood", "confidence": 70}
  ],
  "customers": [
    {"name": "home_office", "confidence": 85}
  ]
}
```

### 6.3 Keyword Clustering Prompt

**Input Schema：**

```json
{
  "seed_keyword": "desk organizer",
  "keywords": [
    "wood desk organizer",
    "office desk storage",
    "minimalist desk decor",
    "rustic pen holder",
    "bamboo desk tray"
  ]
}
```

**Output Schema：**

```json
{
  "clusters": [
    {
      "cluster_id": 1,
      "name": "Wood Desk Organization",
      "keywords": ["wood desk organizer", "rustic pen holder"],
      "confidence": 88
    },
    {
      "cluster_id": 2,
      "name": "Minimalist Office Decor",
      "keywords": ["minimalist desk decor", "bamboo desk tray"],
      "confidence": 75
    }
  ]
}
```

### 6.4 1688 Keyword Generation Prompt

**Input Schema：**

```json
{
  "keyword": "desk organizer",
  "materials": ["wood"],
  "styles": ["rustic"],
  "features": ["drawer", "phone_holder"],
  "customers": ["home_office"]
}
```

**Output Schema：**

```json
{
  "level1": ["桌面收纳盒"],
  "level2": ["木质桌面收纳盒", "实木办公收纳盒"],
  "level3": ["带抽屉桌面收纳盒", "胡桃木桌面整理盒"],
  "material": ["榉木收纳盒", "竹木桌面收纳", "黑胡桃木办公收纳"],
  "factory": ["桌面收纳盒厂家", "办公收纳OEM", "木质文具收纳定制"],
  "scene": ["办公室桌面收纳", "书桌整理盒", "办公桌收纳架"]
}
```

**约束：**

```
- 不翻译英文
- 根据产品特征推导中文词
- 必须包含：一级词、二级词、三级词、材质词、厂家词、场景词
```

---

## 七、人机协作节点

### 7.1 必须人工确认的点

| 节点 | AI 输出 | 人类动作 |
|:---|:---|:---|
| **类目选择** | 推荐主攻类目 | 确认或切换 |
| **Cluster 选择** | 聚类结果 | 选择目标 Cluster |
| **1688 关键词修正** | 生成采购词 | 修改/补充/确认 |
| **最终采购决策** | 评分 + 证据链 | 执行/观察/放弃 |

### 7.2 原则

```
AI 建议
人类决策
系统记录决策结果用于学习
```

---

## 八、1688 数据策略

### 8.1 分阶段方案

| 版本 | 方式 | 状态 | 说明 |
|:---|:---|:---|:---|
| **V1** | 人工上传 CSV | **现在做** | 验证流程，零风险 |
| **V2** | 第三方 API（如有） | 后续 | 1688 开放平台 API |
| **V3** | Playwright 抓取 | 最后考虑 | 反爬风险高，维护成本大 |

### 8.2 Supplier Score

```python
Supplier Score =
    Years       * 0.20 +
    RepeatRate  * 0.30 +
    MOQScore    * 0.20 +   # MOQ < 50 = 10分，50-100 = 7分，>100 = 4分
    OEM         * 0.30      # 支持 = 10分，不支持 = 0分
```

### 8.3 人工录入模板

```csv
supplier_name,supplier_url,unit_cost_cny,moq,repeat_rate,oem,years,product_image_url
实木家居厂,https://1688.com/xxx,18.5,50,35%,1,8,https://img.1688.com/xxx
```

---

## 九、Product DNA（系统核心资产）

### 9.1 定义

```
产品的可复制成功结构
```

### 9.2 结构

```json
{
  "style": "cottagecore",
  "material": "wood",
  "color": "sage green",
  "feature": "drawer",
  "customer": "home office"
}
```

### 9.3 用途

- 跨品类学习（wall art 的 cottagecore 成功 → desk organizer 的 cottagecore 可能成功）
- 趋势分析（哪种 DNA 组合最近成功率高）
- 推荐生成（基于成功 DNA 推荐新产品方向）

---

## 十、学习引擎

### 10.1 目标

让系统越来越聪明。

### 10.2 输入

```
预测分数 vs 实际利润
预测决策 vs 实际决策
```

### 10.3 输出

```
动态权重调整
```

### 10.4 示例

```python
# 如果 cottagecore 风格连续成功
if historical_success_rate('style', 'cottagecore') > 0.7:
    brandfit_weight += 0.02  # 提高品牌匹配权重

# 如果 Margin 预测准确率低于 50%
if margin_prediction_accuracy < 0.5:
    margin_weight -= 0.03  # 降低 Margin 权重，提高其他维度
```

### 10.5 约束

```
权重调整范围：±0.05
每次调整需记录原因
人类可手动覆盖
```

---

## 十一、Phase 实施路线图

### Phase 1（2-4周）：MVP 闭环

**目标：** 跑通从"上传 CSV"到"输出 1688 搜索词"的闭环

| 模块 | 内容 | 状态 |
|:---|:---|:---|
| 数据库 | 创建所有表结构 | 待开发 |
| Category Agent | 3类目 CSV 导入 + 规则评分 | 待开发 |
| Keyword Agent | 种子词扩展 + 聚类 | 待开发 |
| Feature Agent | Top Listings 特征提取 | 待开发 |
| Supply Agent | 1688 关键词生成 | 待开发 |
| 前端 | 上传页面 + 结果展示 | 待开发 |

**不做：**
- Review Agent（Phase 2）
- Winning Pattern Agent（Phase 2）
- Learning Engine（Phase 3）
- 1688 自动化抓取（Phase 2-3）

### Phase 2（1-2个月）：增强

- Review Agent（间接分析）
- Winning Pattern Agent
- Evidence Chain 可视化
- Product DNA 跨品类分析
- 数据库迁移 PostgreSQL（如需）

### Phase 3（3-6个月）：平台化

- Pinterest / Google Trends 接入
- Learning Engine 自动调权
- 1688 V2/V3 自动化
- 多店铺管理

---

## 十二、JSON Schema 契约

### 12.1 Agent 间数据格式

```json
{
  "version": "1.0",
  "agent": "category_agent",
  "input_hash": "sha256:abc123",
  "timestamp": "2026-05-28T10:00:00Z",
  "data": {}
}
```

### 12.2 错误处理

```json
{
  "error": true,
  "error_type": "llm_timeout",
  "message": "DeepSeek API 超时",
  "fallback": "使用规则引擎备用评分"
}
```

---

## 十三、关键结论

### 13.1 系统本质

```
V1 = 工具（关键词分析）
V2 = 分析系统（数据驱动）
V3 = 决策+学习系统（可盈利）
```

### 13.2 赚钱三层结构

```
1. 发现机会（Keyword + Listing）
2. 验证机会（Score + Evidence）
3. 执行机会（1688 + Supplier）
```

### 13.3 如果没有这三个系统

```
Evidence Engine
Product DNA
Learning Engine
```

系统永远只是：

> "聪明的选品工具"

不是：

> "赚钱机器"

---

## 附录：文件清单

| 文件 | 路径 | 说明 |
|:---|:---|:---|
| 本规格书 | `docs/SPEC.md` | 工程基准 |
| PRD | `docs/01_PRD.md` | 产品定义 |
| 数据库Schema | `docs/03_DATABASE_SCHEMA.md` | 详细表结构 |
| Prompt库 | `docs/05_PROMPT_LIBRARY.md` | 所有Agent Prompt |
| 评分引擎 | `docs/06_SCORING_ENGINE.md` | 公式和阈值 |
| 人机协作 | `docs/07_HUMAN_IN_THE_LOOP.md` | 确认节点设计 |
| 1688策略 | `docs/08_1688_DATA_STRATEGY.md` | 分阶段方案 |
| Product DNA | `docs/09_PRODUCT_DNA.md` | 核心资产设计 |
| 学习引擎 | `docs/10_LEARNING_ENGINE.md` | 进化机制 |
| 路线图 | `docs/11_IMPLEMENTATION_ROADMAP.md` | 开发顺序 |
| JSON契约 | `docs/12_JSON_SCHEMA_CONTRACTS.md` | Agent间数据格式 |
