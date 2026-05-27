"""
数据库连接管理
SQLite 单文件，支持路径配置
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库文件路径（可配置）
DB_PATH = os.getenv("MHH_DB_PATH", "./maple_hollow_home.db")

# 创建引擎
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False
)

# 启用外键约束
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """启用 SQLite 外键约束"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
Base = declarative_base()


def get_db():
    """获取数据库会话（生成器，用于 FastAPI Depends）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库：执行 schema.sql（逐条执行）"""
    schema_path = Path(__file__).parent / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    
    # 按分号分割语句，逐条执行
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    
    with engine.connect() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)
        conn.commit()
