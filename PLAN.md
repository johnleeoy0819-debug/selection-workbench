# PLAN.md — Maple Hollow Home v1.0

> 技术实现计划
> 基于 SPEC.md 和 CONSTITUTION.md

---

## 1. 技术架构

```
┌─────────────────────────┐       ┌──────────────────────────────┐
│   Vercel (前端)          │       │   EC2 服务器 (后端)           │
│   ─────────────────────  │       │   IP: 18.234.173.5            │
│   React 19 + Vite 6      │ HTTP  │   ─────────────────────────  │
│   手写 CSS (minimalist)  │◄─────►│   FastAPI :8000               │
│                          │       │   SQLite 数据库                │
│                          │       │   DeepSeek API (OpenRouter)   │
└─────────────────────────┘       └──────────────────────────────┘
         ▲                                    ▲
         │                                    │
    用户浏览器                          OpenCLI 采集结果
    (本地 Mac)                          (用户上传)
```

---

## 2. 项目结构

```
maple-hollow-home/
├── frontend/                    # React + Vite
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/          # 通用组件
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Tag.tsx
│   │   │   ├── ScoreBadge.tsx
│   │   │   └── UploadZone.tsx
│   │   ├── pages/               # 页面
│   │   │   ├── KeywordLab.tsx
│   │   │   ├── ProductValidator.tsx
│   │   │   ├── AIScoring.tsx
│   │   │   ├── ProductPool.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/               # 自定义 Hooks
│   │   │   ├── useApi.ts
│   │   │   └── useProducts.ts
│   │   ├── types/               # TypeScript 类型
│   │   │   └── index.ts
│   │   └── styles/              # CSS
│   │       ├── variables.css
│   │       ├── global.css
│   │       └── components.css
│   └── public/
├── backend/                     # FastAPI
│   ├── main.py                  # 入口
│   ├── requirements.txt
│   ├── database/
│   │   ├── schema.sql           # 数据库 Schema
│   │   ├── models.py            # SQLAlchemy 模型
│   │   └── connection.py        # 数据库连接
│   ├── routers/
│   │   ├── products.py          # 产品 API
│   │   ├── keywords.py          # 关键词 API
│   │   ├── scoring.py           # 评分 API
│   │   ├── compliance.py        # 合规 API
│   │   └── config.py            # 配置 API
│   ├── services/
│   │   ├── csv_importer.py      # CSV 导入
│   │   ├── scoring_engine.py    # 评分引擎
│   │   ├── pricing_calculator.py # 定价计算
│   │   └── ai_client.py         # DeepSeek API 调用
│   ├── models/
│   │   └── schemas.py           # Pydantic 模型
│   └── tests/
│       ├── test_csv_import.py
│       ├── test_scoring.py
│       └── test_pricing.py
├── docs/
│   ├── api-contract.md          # API 契约
│   ├── database-schema.md       # 数据库设计
│   └── ui-design.md             # UI 设计
├── CONSTITUTION.md              # 项目原则
├── SPEC.md                      # 功能规范
├── PLAN.md                      # 本文件
└── README.md                    # 项目说明
```

---

## 3. 模块实现顺序

按依赖关系排序：

| 顺序 | 模块 | 依赖 | 预估时间 |
|------|------|------|---------|
| 1 | 数据库 + 模型 | 无 | 30 min |
| 2 | CSV 导入服务 | 数据库 | 30 min |
| 3 | 定价计算服务 | 无 | 20 min |
| 4 | 评分引擎 | 定价计算 | 30 min |
| 5 | 产品 CRUD API | 数据库 | 30 min |
| 6 | 关键词 API | CSV 导入 | 20 min |
| 7 | 评分 API | 评分引擎 | 20 min |
| 8 | 前端基础（布局+组件） | 无 | 40 min |
| 9 | 关键词工作台页面 | 关键词 API | 30 min |
| 10 | 单品验证台页面 | 产品 API + 定价 | 40 min |
| 11 | AI 评分台页面 | 评分 API | 30 min |
| 12 | 选品池页面 | 产品 API | 30 min |

**总计：约 6-7 小时**

---

## 4. 关键设计决策

### 4.1 数据库
- SQLite 单文件，路径可配置
- SQLAlchemy ORM，支持迁移
- 连接池：单连接（SQLite 限制）

### 4.2 API 设计
- RESTful，JSON 格式
- 统一错误响应：`{ "error": true, "message": "...", "code": "..." }`
- 分页：`?limit=20&offset=0`
- 排序：`?sort=score&order=desc`

### 4.3 前端状态管理
- React Context + useReducer（足够，不用 Redux）
- API 调用封装在 hooks 中
- 本地缓存：sessionStorage

### 4.4 AI 集成
- DeepSeek V4 Pro via OpenRouter
- 结构化 JSON 输出
- 超时：30s
- 重试：3 次

### 4.5 文件上传
- CSV 上传：multipart/form-data
- 1688 结果上传：JSON 或 ZIP
- 限制：10MB

---

## 5. 技术栈版本

| 组件 | 版本 |
|------|------|
| Python | 3.12+ |
| FastAPI | 0.115+ |
| Pydantic | v2 |
| SQLAlchemy | 2.0+ |
| React | 19 |
| Vite | 6 |
| TypeScript | 5.7+ |

---

## 6. 部署计划

### 6.1 前端（Vercel）
```bash
cd frontend
npm install
npm run build
vercel --prod
```

### 6.2 后端（EC2）
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6.3 CORS 配置
```python
origins = [
    "https://maple-hollow-home.vercel.app",
    "http://localhost:5173",  # 开发
]
```

---

## 7. 测试策略

### 7.1 单元测试
- pytest + pytest-asyncio
- 覆盖率目标：80%+

### 7.2 测试文件
| 文件 | 测试内容 |
|------|---------|
| test_csv_import.py | CSV 解析、数据验证 |
| test_scoring.py | 评分计算、权重应用 |
| test_pricing.py | 成本计算、平台费计算 |

### 7.3 集成测试
- API 端到端测试
- 前端组件测试（React Testing Library）

---

## 8. 风险缓解

| 风险 | 缓解措施 |
|------|---------|
| SQLite 并发 | 单用户系统，读写分离 |
| AI API 失效 | 缓存评分结果，支持手动评分 |
| 大 CSV 导入 | 分页处理，进度反馈 |
| 前端构建失败 | 本地开发先用 vite dev |

---

## 9. 任务清单

- [ ] 1. 创建数据库 Schema
- [ ] 2. 创建 SQLAlchemy 模型
- [ ] 3. 实现 CSV 导入服务
- [ ] 4. 实现定价计算服务
- [ ] 5. 实现评分引擎
- [ ] 6. 实现产品 CRUD API
- [ ] 7. 实现关键词 API
- [ ] 8. 实现评分 API
- [ ] 9. 初始化前端项目
- [ ] 10. 创建基础组件
- [ ] 11. 实现关键词工作台页面
- [ ] 12. 实现单品验证台页面
- [ ] 13. 实现 AI 评分台页面
- [ ] 14. 实现选品池页面
- [ ] 15. 编写测试
- [ ] 16. 安全审查
- [ ] 17. 代码审查
- [ ] 18. Git commit + push
