from datetime import datetime

from typing import Optional,List,Sequence
from sqlmodel import Column, Field, SQLModel, Relationship
from pgvector.sqlalchemy import Vector




class Paper(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    authors: str
    published_date: datetime
    topic: str
    local_pdf_path: str
    abstract: str
    arxiv_url: str

    # 后续使用，存储summary和paper的embedding
    summary: str = Field(default = "AI summary not available")
    chunks: list["PaperChunk"] = Relationship(back_populates="paper")

#存切好的paper的chunks
class PaperChunk(SQLModel, table = True):
    id: Optional[int] = Field(default = None, primary_key = True)
    chunk_index : int
    text : str
    metadata_json: str

    #外键
    paper_id : str = Field(foreign_key="paper.id")
    paper: Paper = Relationship(back_populates="chunks")

    #vectors
    embedding: Sequence[float] | None = Field(default=None, sa_column=Column(Vector(1536)))
