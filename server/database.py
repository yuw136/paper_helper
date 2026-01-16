# database.py
from sqlmodel import SQLModel, create_engine
from sqlalchemy import text

#建表需要import所有表对应的类
from models.paper import Paper

# 这里的 URL 对应 docker 启动的设置
DATABASE_URL = "postgresql://user:password@localhost:5432/paper_helper"

# echo=True 会打印出生成的 SQL 语句
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    # 启用 pgvector 扩展
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    # 扫描所有继承了 SQLModel 的类，并在数据库创建表
    SQLModel.metadata.create_all(engine)