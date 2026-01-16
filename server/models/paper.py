from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel



class Paper(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    authors: str
    published_date: datetime
    category: str
    local_pdf_path: str
    abstract: str

    # 后续使用，存储summary和paper的embedding
    summary: str = Field(default = "AI summary not available")
    embedding: list[float] | None = Field(
        default=None, sa_column=Column(Vector(1536))
    )
