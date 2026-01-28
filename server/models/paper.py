from datetime import datetime

from typing import Optional,List,Sequence
from sqlmodel import Column, Field, SQLModel, Relationship
from pgvector.sqlalchemy import Vector

class Paper(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    authors: str = Field(default=None)
    published_date: datetime = Field(default=None)
    topic: str = Field(default=None)
    
    #local file path for showing file tree in frontend
    local_pdf_path: str
    storage_url: Optional[str] = Field(default=None)
    
    abstract: str = Field(default=None)
    arxiv_url: str = Field(default=None)

    summary: str = Field(default = "AI summary not available")
    chunks: list["PaperChunk"] = Relationship(back_populates="paper")


class PaperChunk(SQLModel, table = True):
    id: Optional[int] = Field(default = None, primary_key = True)
    chunk_index : int
    text : str
    metadata_json: str

    #foreign key
    paper_id : str = Field(foreign_key="paper.id")
    paper: Paper = Relationship(back_populates="chunks")

    #vectors
    embedding: Sequence[float] | None = Field(default=None, sa_column=Column(Vector(1536)))
