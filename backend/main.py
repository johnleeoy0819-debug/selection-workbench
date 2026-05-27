"""
Maple Hollow Home - FastAPI 入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import init_db
from routers import keywords, products, scoring, pricing

app = FastAPI(
    title="Maple Hollow Home",
    description="Etsy 选品决策工作台",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://maple-hollow-home.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
def startup():
    init_db()

# 注册路由
app.include_router(keywords.router)
app.include_router(products.router)
app.include_router(scoring.router)
app.include_router(pricing.router)


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "version": "1.0.0"}
