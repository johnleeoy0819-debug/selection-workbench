# AGENTS.md — 选品工作台

> 本文档供 AI 编程助手（Claude Code / Cursor / Copilot）自动加载。
> 包含项目全部架构决策、设计规范、开发约定。
> 文件位置：仓库根目录，任何 AI 工具进入项目自动读取。

---

## 项目定位

Etsy 选品闭环系统。用户 Lee，零经验起步，第一款产品是「挂钩 (Hook)」。
目标：从 eRank 数据导入 → 竞品分析 → 1688 采集 → 利润评分 → 合规检查 → 排行榜展示的完整闭环。

---

## 架构决策

```
前端：Vercel（静态 HTML/CSS/JS）→ 免费、全球 CDN
后端：EC2 18.234.173.5（FastAPI :8000）→ 能跑长时间任务、开 Chrome
通信：HTTP REST API
```

**为什么不分层部署：**
- Vercel Serverless 有 10s 超时，无法做 1688 采集（需要真实浏览器，耗时 30s+）
- OpenCLI 需要 Chrome 进程常驻，只能跑在 EC2
- 前端纯静态，Vercel 免费且快
- Memory Tree + SQLite + Cron 都在 EC2

---

## 设计系统

**唯一风格：minimalist-ui**

```css
/* 核心变量 */
--bg: #F7F6F3;          /* 暖白底色，不是纯白 */
--border: #EAEAEA;      /* 1px 浅灰 */
--text: #111111;        /* 纯黑，不用 #333 */
--accent: #111111;      /* 按钮和强调也是黑色 */
--radius: 8px;          /* 统一圆角 */
```

**硬规则：**
- ❌ 禁止渐变
- ❌ 禁止阴影（box-shadow / drop-shadow）
- ❌ 禁止 emoji 作为 UI 元素
- ❌ 禁止 Inter / Roboto / Arial
- ✅ 字体：Instrument Serif（标题）+ Instrument Sans（正文）
- ✅ 层次靠排版（字号/字重/间距），不靠颜色
- ✅ 按钮纯黑 #111，无阴影
- ✅ 标签：浅色背景 + 大写字母 + 宽间距
- ✅ 移动端：768px / 400px 两个断点，表格横向滚动

**参考文件：** `docs/minimalist-ui-reference.html`

---

## API 契约

后端基础 URL：`http://18.234.173.5:8000`

| 端点 | 方法 | 请求 | 响应 |
|------|------|------|------|
| `/api/products` | GET | `?sort=score&limit=20` | 产品列表 JSON |
| `/api/products/:id` | GET | - | 单品详情 |
| `/api/products/import` | POST | CSV 文件上传 | 导入结果 |
| `/api/keywords` | GET | `?category=hook` | 关键词分析 |
| `/api/compliance/:id` | GET | - | 合规检查结果 |
| `/api/scoring/:id` | GET | - | 评分明细 |

**评分维度：** 市场机会 × 利润空间 × 竞争度 × 合规性 × 1688 可采购性

---

## 1688 采集

**方式：** OpenCLI（真实 Chrome 浏览器，非 API 爬虫）
**原因：** 1688 有严格反爬，服务端请求会被拦截
**限制：** 需要用户 Mac 本地运行（OpenCLI 操控本地 Chrome）
**数据流：** 本地采集 → 上传 JSON → 后端入库 → 评分引擎

---

## 合规红线（Etsy 政策）

- ❌ 不能直接转售 1688 成品
- ✅ 必须有设计参与：定制尺寸/颜色/logo/材质组合
- ✅ 必须公开 Production Partner
- ✅ 改造不能仅限于换包装

---

## 技术栈

```
前端：纯 HTML/CSS/JS（无框架，减少依赖）
后端：Python 3.11+ / FastAPI / SQLite / Pydantic
采集：OpenCLI（Node.js，真实浏览器）
LLM：DeepSeek（评分、分析、合规）
记忆：Memory Tree Pipeline + agentmemory
```

---

## 开发约定

1. **API 优先**：先定义契约，再实现
2. **模块独立**：每个模块有明确的输入/输出 JSON
3. **无状态函数**：后端 API 不依赖 session
4. **文件名小写**：`scoring.py` 不是 `Scoring.py`
5. **类型标注**：所有 Python 函数必须标注参数和返回值类型
6. **Docstring**：每个 public 函数必须有 docstring（中文）

---

## 当前状态

- [x] 架构决策完成
- [x] 设计风格确定（minimalist-ui）
- [x] 设计预览通过
- [ ] Phase 1：后端 API 骨架
- [ ] Phase 2：前端仪表盘
- [ ] Phase 3：数据导入模块
- [ ] Phase 4：评分引擎
- [ ] Phase 5：1688 采集接入
