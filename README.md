# 选品工作台 (Selection Workbench)

> Etsy 选品闭环系统 — 从 eRank 数据导入、竞品分析、关键词推荐，到 1688 采集、利润评分、合规检查、排行榜展示。

**当前版本:** v0.1 · Phase 0 项目初始化

---

## 架构

```
┌─────────────────────────┐       ┌──────────────────────────────┐
│   Vercel (前端)          │       │   EC2 服务器 (后端)           │
│   ─────────────────────  │       │   IP: 18.234.173.5            │
│   静态 HTML/CSS/JS       │ HTTP  │   ─────────────────────────  │
│   全球 CDN · 免费        │◄─────►│   FastAPI :8000               │
│   minimalist-ui 风格     │       │   + OpenCLI 采集              │
│                          │       │   + Memory Tree 记忆           │
│                          │       │   + SQLite 数据存储             │
└─────────────────────────┘       └──────────────────────────────┘
```

| 层 | 部署 | 职责 |
|---|------|------|
| 前端 | Vercel | 仪表盘、排行榜、设置页面 |
| 后端 | EC2 (这台) | API、1688 采集、评分引擎、数据存储 |

---

## 技术栈

**前端**
- 纯 HTML/CSS/JavaScript（无框架）
- 设计系统：minimalist-ui
- 部署：Vercel（自动从 GitHub 部署）

**后端**
- Python 3.11+ / FastAPI
- 数据库：SQLite
- 采集：OpenCLI（真实浏览器，操作 1688）
- 记忆：Memory Tree Pipeline + agentmemory
- LLM：DeepSeek（评分、分析、合规检查）

---

## 项目结构

```
selection-workbench/
├── frontend/                # Vercel 部署的前端
│   ├── index.html           # 仪表盘主页
│   ├── css/
│   │   └── minimalist.css   # minimalist-ui 样式系统
│   ├── js/
│   │   ├── api.js           # 后端 API 调用封装
│   │   └── dashboard.js     # 仪表盘逻辑
│   └── pages/
│       ├── ranking.html     # 排行榜
│       ├── detail.html      # 单品详情
│       └── settings.html    # 设置
├── backend/                 # EC2 部署的后端
│   ├── main.py              # FastAPI 入口
│   ├── api/
│   │   ├── products.py      # 产品 CRUD
│   │   ├── scoring.py       # 评分引擎
│   │   ├── keywords.py      # 关键词分析
│   │   └── compliance.py    # 合规检查
│   ├── services/
│   │   ├── collector.py     # 1688 采集 (OpenCLI)
│   │   ├── erank.py         # eRank CSV 解析
│   │   └── scorer.py        # 评分算法
│   ├── models/
│   │   └── schemas.py       # Pydantic 模型
│   └── tests/
├── docs/
│   ├── api-contract.md      # API 契约
│   └── frontend-guide.md    # 前端开发规范
└── README.md
```

---

## 开发流程

1. Clone 仓库到本地 Mac
2. 后端：本地 `uvicorn main:app --reload` 开发
3. 前端：直接打开 HTML 文件开发，调后端 API
4. 提交 → GitHub → Vercel 自动部署前端 / EC2 手动部署后端

---

## 第一期 MVP 范围

- [ ] 数据导入：上传 eRank CSV，解析入库
- [ ] 排行榜：综合评分排序展示
- [ ] 单品详情：成本、利润、合规、关键词
- [ ] 关键词分析表格
- [ ] 合规检查清单

---

## 设计规范

**风格：** [minimalist-ui](docs/frontend-guide.md)
- 暖白底色 #F7F6F3 · 1px 边框 · 无阴影无渐变
- 字体：Instrument Serif（标题）+ Instrument Sans（正文）
- 按钮：纯黑 #111 · 圆角 8px
- 移动端响应式（768px/400px 断点）

---

## 后端 API 概览

详见 [docs/api-contract.md](docs/api-contract.md)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/products` | GET | 产品列表（支持排序、筛选） |
| `/api/products/:id` | GET | 单品详情 |
| `/api/products/import` | POST | 导入 eRank CSV |
| `/api/keywords` | GET | 关键词分析数据 |
| `/api/compliance/:id` | GET | 合规检查结果 |
| `/api/scoring/:id` | GET | 评分明细 |
